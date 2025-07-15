import os
import re
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from bs4 import BeautifulSoup

from api.models import Race, Horse, Jockey, Trainer, Entry


# ============ 共通ヘルパ ============ #
def parse_sex_age(sex_age_str: str):
    if not sex_age_str:
        return None, None
    return sex_age_str[0], (
        int(re.search(r"\d+", sex_age_str).group())
        if re.search(r"\d+", sex_age_str)
        else None
    )


def parse_horse_weight(weight_str: str):
    if not weight_str or weight_str.strip("-") == "":
        return None, None
    m = re.match(r"^(\d+)\s*(?:$([-+]?\d+)$)?$", weight_str)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2)) if m.group(2) else None


def to_int(val):
    try:
        return int(val.replace(",", ""))
    except Exception:
        return None


def to_float(val):
    try:
        return float(val.replace(",", ""))
    except Exception:
        return None


# ============ スクレイパ ============ #
class NetkeibaRaceAnalyzer:
    WAIT_SEC = 10

    def __init__(self, headless=True):
        opts = webdriver.ChromeOptions()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("start-maximized")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        )

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=opts
        )

        stealth(
            self.driver,
            languages=["ja-JP", "ja"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    # ------------------------------------------------------------------ #
    def close(self):
        if self.driver:
            self.driver.quit()

    # ------------------------------------------------------------------ #
    def scrape(self, race_id: str):
        url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"
        self.driver.get(url)

        try:
            WebDriverWait(self.driver, self.WAIT_SEC).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.RaceName"))
            )
        except Exception as e:
            raise RuntimeError(f"ページロードタイムアウト: {e}")

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        main_info = self._parse_main_info(soup, race_id)
        entries = self._parse_entries(soup)
        return main_info, entries

    # --------------- private --------------- #
    def _parse_main_info(self, soup, race_id):
        race_name_tag = soup.select_one("h1.RaceName")
        race_data01 = soup.select_one("div.RaceData01")
        race_data02_span = soup.select_one("div.RaceData02 span")

        if not (race_name_tag and race_data01):
            raise RuntimeError("RaceName または RaceData01 が取得できません")

        race_name = race_name_tag.text.strip()

        m = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日)", race_data01.text)
        if not m:
            raise RuntimeError("開催日付が取得できません")
        race_date = datetime.datetime.strptime(m.group(1), "%Y年%m月%d日").date()

        venue = None
        parts = race_data01.text.split()
        if len(parts) > 1:
            venue = parts[1]

        course_details = ground_condition = None
        if race_data02_span:
            tmp = race_data02_span.text.strip().split("/")
            if tmp:
                course_details = tmp[0].strip()
            if len(tmp) > 1 and ":" in tmp[-1]:
                ground_condition = tmp[-1].split(":")[-1].strip()

        return dict(
            race_id=race_id,
            race_name=race_name,
            race_date=race_date,
            venue=venue,
            course_details=course_details,
            ground_condition=ground_condition,
        )

    def _parse_entries(self, soup):
        table = soup.select_one("table.Shutuba_Table, table.RegHorse_Table")
        if not table:
            return []

        entries = []
        for tr in table.select("tbody tr"):
            tds = tr.find_all("td")
            if len(tds) < 10:
                continue

            horse_link = tds[3].select_one("a[href*='/horse/']")
            jockey_link = tds[6].select_one("a[href*='/jockey/']")
            trainer_link = tds[7].select_one("a[href*='/trainer/']")

            entry = {
                "waku": tds[0].get_text(strip=True),
                "umaban": tds[1].get_text(strip=True),
                "horse_id": (
                    re.search(r"/horse/(\d+)", horse_link["href"]).group(1)
                    if horse_link
                    else None
                ),
                "horse_name": tds[3].get_text(strip=True),
                "sex_age": tds[4].get_text(strip=True),
                "weight_carried": tds[5].get_text(strip=True),
                "jockey_id": (
                    re.search(r"/jockey/.+?/(\d+)", jockey_link["href"]).group(1)
                    if jockey_link
                    else None
                ),
                "jockey_name": tds[6].get_text(strip=True),
                "trainer_id": (
                    re.search(r"/trainer/.+?/(\d+)", trainer_link["href"]).group(1)
                    if trainer_link
                    else None
                ),
                "trainer_name": tds[7].get_text(strip=True),
                "horse_weight_str": tds[8].get_text(strip=True),
                "odds": tds[9].get_text(strip=True),
            }
            entries.append(entry)
        return entries


# ============ Django Management Command ============ #
class Command(BaseCommand):
    help = "指定 race_id の出馬表を取得し DB に保存"

    def add_arguments(self, parser):
        parser.add_argument("race_id", type=str, help="例: 202305020811 (12桁)")

    # ---------------- handle ---------------- #
    def handle(self, *args, **opts):
        race_id = opts["race_id"]
        headless = os.getenv("SCRAPE_HEADLESS", "1") == "1"

        self.stdout.write(
            self.style.NOTICE(f"▶ {race_id} 取得開始 (headless={headless})")
        )

        analyzer = NetkeibaRaceAnalyzer(headless=headless)
        try:
            main_info, entries = analyzer.scrape(race_id)
        except Exception as e:
            analyzer.close()
            raise CommandError(f"スクレイピング失敗: {e}")

        self.stdout.write(self.style.SUCCESS("▷ HTML 解析完了"))

        if not main_info or not entries:
            analyzer.close()
            raise CommandError("レース情報または出走表が取得できませんでした")

        try:
            with transaction.atomic():
                self._save_to_db(main_info, entries)
        finally:
            analyzer.close()

        self.stdout.write(self.style.SUCCESS("★ 完了"))

    # ---------------- DB helper ---------------- #
    def _save_to_db(self, main, entries):
        race_obj, _ = Race.objects.update_or_create(
            race_id=main["race_id"],
            defaults=dict(
                race_name=main["race_name"],
                race_date=main["race_date"],
                venue=main["venue"],
                course_details=main["course_details"],
                ground_condition=main["ground_condition"],
            ),
        )

        for e in entries:
            if not e["horse_id"]:
                continue

            sex, age = parse_sex_age(e["sex_age"])

            horse_obj, _ = Horse.objects.update_or_create(
                horse_id=e["horse_id"],
                defaults=dict(
                    horse_name=e["horse_name"],
                    sex=sex,
                    age=age,
                ),
            )

            jockey_obj = None
            if e["jockey_id"]:
                jockey_obj, _ = Jockey.objects.update_or_create(
                    jockey_id=e["jockey_id"],
                    defaults=dict(jockey_name=e["jockey_name"]),
                )

            trainer_obj = None
            if e["trainer_id"]:
                trainer_obj, _ = Trainer.objects.update_or_create(
                    trainer_id=e["trainer_id"],
                    defaults=dict(trainer_name=e["trainer_name"]),
                )
                # 馬に調教師を紐づけ
                if not horse_obj.trainer:
                    horse_obj.trainer = trainer_obj
                    horse_obj.save(update_fields=["trainer"])

            horse_weight, horse_weight_diff = parse_horse_weight(e["horse_weight_str"])

            Entry.objects.update_or_create(
                race=race_obj,
                horse=horse_obj,
                defaults=dict(
                    jockey=jockey_obj,
                    waku=to_int(e["waku"]),
                    umaban=to_int(e["umaban"]),
                    weight_carried=to_float(e["weight_carried"]),
                    odds=to_float(e["odds"]),
                    horse_weight=horse_weight,
                    horse_weight_diff=horse_weight_diff,
                ),
            )

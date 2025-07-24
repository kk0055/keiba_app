import os
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import argparse
import datetime
from django.core.management.base import BaseCommand
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service

from api.models import Race, Horse, Jockey, Trainer, Entry, HorsePastRace


class Command(BaseCommand):
    help = "指定した race_id のレース情報を取得します"

    def add_arguments(self, parser):
        parser.add_argument(
            "race_id", type=str, help="取得したいレースID（例: 202406030811）"
        )
        parser.add_argument(
            "--entry-only",
            action="store_true",
            help="エントリー情報のみをスクレイピングします。",
        )

    def handle(self, *args, **options):
        race_id = options["race_id"]
        entry_only = options["entry_only"]
        main(race_id, entry_only)


def main(race_id: str, entry_only=False):
    analyzer = None
    try:
        analyzer = NetkeibaRaceAnalyzer()
        analyzer.get_race_entry(race_id, entry_only)

        print("\n=== 処理完了 ===")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
    finally:
        if analyzer:
            analyzer.close()


class NetkeibaRaceAnalyzer:
    def __init__(self):
        options = webdriver.ChromeOptions()

        options.add_argument("--headless")  # ヘッドレスモード
        options.add_argument(
            "--window-size=1920,1080"
        )  # ヘッドレスモードで要素を正しく認識させるため
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        options.add_argument("--disable-gpu")  # GPU無効化 (Windows)
        options.add_argument("--disable-dev-shm-usage")  # Linux環境なら
        # 画像を無効化する設定
        options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(
            service=service,
            options=options,
        )
        self.db_base_url = "https://db.netkeiba.com"

    def close(self):
        if self.driver:
            self.driver.quit()

    def get_race_entry(self, race_id, entry_only):
        url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"
        print(f"出馬表URLにアクセス: {url}")
        try:
            self.driver.get(url)
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "HorseList"))
                )
                self.driver.find_element(By.CLASS_NAME, "HorseList")

                print("HorseListが見つかりました。処理を続行します。")

            except NoSuchElementException:
                print(
                    "HorseListが見つかりませんでした。無効なページのため処理を終了します。"
                )
                return

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "table[class*='RaceTable']")
                )
            )
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            race_name_tag = soup.select_one("h1.RaceName")
            race_data01 = soup.select_one("div.RaceData01")

            venue_spans = soup.find("div", class_="RaceData02").find_all("span")
            venue = venue_spans[1].get_text(strip=True)
            if not (race_name_tag and race_data01):
                raise RuntimeError("RaceName または RaceData01 が取得できません")
            course_details = race_data01.find("span").get_text(strip=True)
            race_name = race_name_tag.text.strip()
            race_num_span = soup.select_one("div.RaceList_Item01 > span.RaceNum")
            if race_num_span:
                text_nodes = [t for t in race_num_span.contents if isinstance(t, str)]
                race_text = "".join(text_nodes).strip()  # '11R'
                number_match = re.search(r"\d+", race_text)
                if number_match:
                    race_number = number_match.group()
            dd = soup.find("dd", class_="Active")
            a_tag = dd.find("a")
            if not a_tag:
                raise RuntimeError("開催日付のタグが見つかりません")

            date_text = a_tag.contents[0].strip()
            year = race_id[:4]
            full_date = f"{year}年{date_text}"
            race_date = datetime.strptime(full_date, "%Y年%m月%d日").date()

            race, created = Race.objects.update_or_create(
                race_id=race_id,
                defaults={
                    "race_name": race_name,
                    "race_date": race_date,
                    "venue": venue,
                    "course_details": course_details,
                    "race_number": race_number,
                },
            )
            if created:
                print(f"{race_id} をDBに新規作成しました。")
            else:
                print(f"既存レース [{race_name}] ({race_id}) の情報を更新しました。")

            table = soup.find("table", class_=["Shutuba_Table", "RegHorse_Table"])
            if not table:
                print("-> 出馬表または登録馬テーブルが見つかりませんでした。")
                return []

            rows = table.select("tbody tr")

            for row in rows:
                cells = row.find_all("td")

                # 取得しようとするデータが存在しない可能性を考慮する
                horse_link = cells[3].find("a") if len(cells) > 3 else None
                horse_name = (
                    horse_link.text.strip() if horse_link else cells[3].text.strip()
                )
                horse_id = (
                    re.search(r"/horse/(\d+)", horse_link["href"]).group(1)
                    if horse_link and "href" in horse_link.attrs
                    else ""
                )
                # jockeyの処理
                jockey_link = cells[6].find("a") if len(cells) > 6 else None
                jockey_id = (
                    re.search(
                        r"/jockey/(?:result/\w+/)?(\d+)", jockey_link["href"]
                    ).group(1)
                    if jockey_link and "href" in jockey_link.attrs
                    else ""
                )

                waku = cells[0].text.strip() if len(cells) > 0 else ""
                umaban = cells[1].text.strip() if len(cells) > 1 else ""
                sex_age = cells[4].text.strip() if len(cells) > 4 else ""
                weight_carried = cells[5].text.strip() if len(cells) > 5 else ""
                jockey_name = cells[6].text.strip() if len(cells) > 6 else ""
                trainer_name = cells[7].text.strip() if len(cells) > 7 else ""
                horse_weight = cells[8].text.strip() if len(cells) > 8 else ""
                odds = cells[9].text.strip() if len(cells) > 9 else ""
                popularity = cells[10].text.strip() if len(cells) > 10 else ""

                weight_to_save = None
                try:
                    weight_to_save = float(weight_carried)
                except (ValueError, TypeError):
                    print(f"斤量が数値でないためスキップします: '{weight_carried}'")

                data = {
                    "race_id": race_id,
                    "waku": waku,
                    "umaban": umaban,
                    "horse_name": horse_name,
                    "horse_id": horse_id,
                    "jockey_id": jockey_id,
                    "sex_age": sex_age,
                    "weight_carried": weight_to_save,
                    "jockey_name": jockey_name,
                    "trainer_name": trainer_name,
                    "horse_weight": horse_weight,
                    "odds": odds,
                    "popularity": popularity,
                }

                horse, created = Horse.objects.get_or_create(
                    horse_id=data["horse_id"],
                    defaults={"horse_name": data["horse_name"]},
                )
                Jockey.objects.get_or_create(
                    jockey_id=jockey_id,
                    defaults={"jockey_name": jockey_name},
                )

                entry, created = Entry.objects.update_or_create(
                    race_id=data["race_id"],
                    horse_id=data["horse_id"],
                    defaults={
                        "jockey_id": data["jockey_id"],
                        "waku": to_int_or_none(data["waku"]),
                        "umaban": to_int_or_none(data["umaban"]),
                        "weight_carried": data["weight_carried"],
                        "odds": data["odds"],
                        "popularity": to_int_or_none(data["popularity"]),
                    },
                )
                if not entry_only:
                    self.get_past_races(horse)

        except Exception as e:
            print(f"出馬表取得中にエラー: {e}")
            return []

    def get_past_races(self, horse, limit=10):
        horse_id = horse.horse_id
        horse_name = horse.horse_name
        print("\n=== 馬情報取得開始 ===")
        print(f"{horse_name}")
        if not horse_id:
            return []
        url = f"{self.db_base_url}/horse/{horse_id}/"
        time.sleep(1)

        horse, _ = Horse.objects.get_or_create(
            horse_id=horse_id, defaults={"horse_name": horse_name}
        )
        try:
            self.driver.get(url)
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            rows = soup.select(".db_h_race_results tbody tr")[:limit]
            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 24:
                    continue

                past_jockey_cell = cells[12]
                past_jockey_link = past_jockey_cell.find("a")

                if past_jockey_link and past_jockey_link.has_attr("href"):
                    # 過去レースの騎手名とIDをリンクから取得
                    past_jockey_name = past_jockey_link.text.strip()
                    past_jockey_id_match = re.search(
                        r"/jockey/result/recent/(\d+)", past_jockey_link["href"]
                    )
                    past_jockey_id = (
                        past_jockey_id_match.group(1) if past_jockey_id_match else None
                    )
                else:
                    # リンクがない場合（地方騎手など）は、名前のみ取得しIDはNoneとする
                    past_jockey_name = past_jockey_cell.text.strip()
                    past_jockey_id = None

                if not past_jockey_id:
                    print(
                        f"  -> 騎手IDが取得できませんでした。スキップします。(騎手名: {past_jockey_name})"
                    )
                    continue

                race_link = cells[4].find("a")
                past_race_id_match = (
                    re.search(r"/race/(\d+)", race_link["href"]) if race_link else None
                )
                venue_raw = cells[1].text.strip()
                match = re.match(r"(\d+)([^\d]+)(\d+)", venue_raw)
                if match:
                    venue_round = int(match.group(1))  # 開催回（例: 3）
                    venue_name = match.group(2)  # 開催地（例: 阪神）
                    venue_day = int(match.group(3))  # 日目（例: 1）
                else:
                    venue_round = None
                    venue_name = venue_raw
                    venue_day = None

                last_3f_rank = None
                class_list = cells[22].get("class", [])
                for cls in class_list:
                    if cls.startswith("rank_"):
                        # 'rank_' の部分を取り除いて数字だけにする
                        last_3f_rank = int(cls.replace("rank_", ""))
                        break

                result_data = {
                    "date": cells[0].text.strip(),
                    "venue_round": venue_round,
                    "venue_name": venue_name,
                    "venue_day": venue_day,
                    "weather": cells[2].text.strip(),
                    "race_name": race_link.text.strip() if race_link else "",
                    "past_race_id": (
                        past_race_id_match.group(1) if past_race_id_match else ""
                    ),
                    "head_count": cells[6].text.strip(),
                    "umaban": cells[7].text.strip(),
                    "waku": cells[8].text.strip(),
                    "odds": cells[9].text.strip(),
                    "popularity": cells[10].text.strip(),
                    "rank": cells[11].text.strip(),
                    "jockey_name": cells[12].text.strip(),
                    "weight_carried": cells[13].text.strip(),
                    "distance": cells[14].text.strip(),
                    "ground_condition": cells[15].text.strip(),
                    "time": cells[17].text.strip(),
                    "margin": cells[18].text.strip(),
                    "passing": cells[20].text.strip(),
                    "pace": cells[21].text.strip(),
                    "last_3f": cells[22].text.strip(),
                    "body_weight": cells[23].text.strip(),
                }
                # print(result_data)
                Jockey.objects.update_or_create(
                    jockey_id=past_jockey_id,
                    defaults={"jockey_name": result_data["jockey_name"]},
                )

                HorsePastRace.objects.update_or_create(
                    horse=horse,
                    past_race_id=result_data["past_race_id"],
                    defaults={
                        "race_date": parse_date(result_data["date"]),
                        "venue_round": result_data["venue_round"],
                        "venue_name": result_data["venue_name"],
                        "venue_day": result_data["venue_day"],
                        "race_name": result_data["race_name"],
                        "race_grade_score": get_race_grade_score(
                            result_data["race_name"]
                        ),
                        "weather": result_data["weather"],
                        "head_count": to_int_or_none(result_data["head_count"]),
                        "waku": to_int_or_none(result_data["waku"]),
                        "umaban": to_int_or_none(result_data["umaban"]),
                        "odds": to_float_or_none(result_data["odds"]),
                        "popularity": to_int_or_none(result_data["popularity"]),
                        "rank": to_int_or_none(result_data["rank"]),
                        "jockey_id": past_jockey_id,
                        "jockey_name": past_jockey_name,
                        "weight_carried": result_data["weight_carried"],
                        "distance": result_data["distance"],
                        "ground_condition": result_data["ground_condition"],
                        "time": result_data["time"],
                        "margin": result_data["margin"],
                        "passing": result_data["passing"],
                        "pace": result_data["pace"],
                        "last_3f": result_data["last_3f"],
                        "last_3f_rank": last_3f_rank,
                        "body_weight": result_data["body_weight"],
                    },
                )
            print(f"  -> {horse_name} の過去レース情報取得完了")
        except Exception as e:
            print(f"  -> 馬の成績取得エラー (ID: {horse_id}): {e}")
            return []

def get_race_grade_score(race_name: str) -> int:
    """
    レース名に含まれるグレード文字列から、対応するスコアを返す関数。
    """
    # GI と JpnI は同等の価値として扱う
    if re.search(r"\(GI\)|\(JpnI\)", race_name, re.IGNORECASE):
        return 100
    # GII と JpnII は同等の価値として扱う
    elif re.search(r"\(GII\)|\(JpnII\)", race_name, re.IGNORECASE):
        return 80
    # GIII と JpnIII は同等の価値として扱う
    elif re.search(r"\(GIII\)|\(JpnIII\)", race_name, re.IGNORECASE):
        return 60
    elif re.search(r"\(L\)", race_name, re.IGNORECASE):
        return 50
    # オープン特別 (OP)
    elif re.search(r"\(OP\)", race_name, re.IGNORECASE):
        return 40
    # 条件戦
    elif "3勝クラス" in race_name:
        return 30
    elif "2勝クラス" in race_name:
        return 20
    elif "1勝クラス" in race_name:
        return 10
    # 新馬・未勝利戦
    elif "新馬" in race_name or "未勝利" in race_name:
        return 5
    else:
        return 0  # 該当しない場合は0

def to_int_or_none(value):
    try:
        return int(value) if value and value.strip().isdigit() else None
    except:
        return None


def to_float_or_none(value):
    try:
        return float(value) if value else None
    except:
        return None


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y/%m/%d").date()
    except:
        return None

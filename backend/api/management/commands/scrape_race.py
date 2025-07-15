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

from api.models import Race, Horse, Jockey, Trainer, Entry, HorsePastRace


class Command(BaseCommand):
    help = "指定した race_id のレース情報を取得します"

    def add_arguments(self, parser):
        parser.add_argument(
            "race_id", type=str, help="取得したいレースID（例: 202406030811）"
        )

    def handle(self, *args, **options):
        race_id = options["race_id"]
        # main関数を呼び出す（race_id を引数として渡す）
        main(race_id)


class NetkeibaRaceAnalyzer:
    def __init__(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # ヘッドレスモード
        # options.add_argument('--window-size=1920,1080') # ヘッドレスモードで要素を正しく認識させるため
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.db_base_url = "https://db.netkeiba.com"

    def close(self):
        if self.driver:
            self.driver.quit()

    def get_race_entry(self, race_id):
        url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"
        print(f"出馬表URLにアクセス: {url}")
        try:
            self.driver.get(url)
            try:
                error_box = self.driver.find_element(By.CLASS_NAME, "Race_Error_Box")
                if error_box:
                    print(
                        "-> エラー: レース情報が見つかりませんでした。指定されたrace_idが正しいか確認してください。"
                    )
                    return []
            except:
                # エラーボックスがなければ正常なので、何もしない
                pass
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
            course_details = race_name_tag.find("span").get_text(strip=True)
            race_name = race_name_tag.text.strip()

            dd = soup.find("dd", class_="Active")
            a_tag = dd.find("a")
            if not a_tag:
                raise RuntimeError("開催日付のタグが見つかりません")
            date_text = a_tag.contents[0].strip()
            year = race_id[:4]
            full_date = f"{year}年{date_text}"
            race_date = datetime.strptime(full_date, "%Y年%m月%d日").date()

            race, created = Race.objects.get_or_create(
                race_id=race_id,
                defaults={
                    "race_name": race_name,
                    "race_date": race_date,
                    "venue": venue,
                    "course_details": course_details,
                },
            )
            if created:
                print(f"{race_id} をDBに新規作成しました。")
            else:
                print(f"{race_id} はすでにDBに存在します。スキップします。")

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

                waku = cells[0].text.strip() if len(cells) > 0 else ""
                umaban = cells[1].text.strip() if len(cells) > 1 else ""
                sex_age = cells[4].text.strip() if len(cells) > 4 else ""
                weight_carried = cells[5].text.strip() if len(cells) > 5 else ""
                jockey_name = cells[6].text.strip() if len(cells) > 6 else ""
                trainer_name = cells[7].text.strip() if len(cells) > 7 else ""
                horse_weight = cells[8].text.strip() if len(cells) > 8 else ""
                odds = cells[9].text.strip() if len(cells) > 9 else ""
                popularity = cells[10].text.strip() if len(cells) > 10 else ""

                data = {
                    "race_id": race_id,
                    "waku": waku,
                    "umaban": umaban,
                    "horse_name": horse_name,
                    "horse_id": horse_id,
                    "sex_age": sex_age,
                    "weight_carried": weight_carried,
                    "jockey_name": jockey_name,
                    "trainer_name": trainer_name,
                    "horse_weight": horse_weight,
                    "odds": odds,
                    "popularity": popularity,
                }
                # entries.append(entry)

                horse, created = Horse.objects.get_or_create(
                    horse_id=data["horse_id"],
                    defaults={"horse_name": data["horse_name"]},
                )

                entry, created = Entry.objects.get_or_create(
                    race_id=data["race_id"],
                    horse_id=data["horse_id"],
                    defaults={
                        "waku": to_int_or_none(data["waku"]),
                        "umaban": to_int_or_none(data["umaban"]),
                        "weight_carried": data["weight_carried"],
                        "odds": data["odds"],
                        "popularity": to_int_or_none(data["popularity"]),
                    },
                )

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
            results = []
            rows = soup.select(".db_h_race_results tbody tr")[:limit]
            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 20:
                    continue
                race_link = cells[4].find("a")
                past_race_id_match = (
                    re.search(r"/race/(\d+)", race_link["href"]) if race_link else None
                )
                result_data = {
                    "date": cells[0].text.strip(),
                    "venue": cells[1].text.strip(),
                    "weather": cells[2].text.strip(),
                    "race_name": race_link.text.strip() if race_link else "",
                    "past_race_id": (
                        past_race_id_match.group(1) if past_race_id_match else ""
                    ),
                    # "track_type": cells[4].text.strip(),
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
                print(result_data)
                HorsePastRace.objects.update_or_create(
                    horse=horse,
                    past_race_id=result_data["past_race_id"],
                    defaults={
                        "race_date": parse_date(result_data["date"]),
                        "venue": result_data["venue"],
                        "race_name": result_data["race_name"],
                        "weather": result_data["weather"],
                        "head_count": to_int_or_none(result_data["head_count"]),
                        "waku": to_int_or_none(result_data["waku"]),
                        "umaban": to_int_or_none(result_data["umaban"]),
                        "odds": to_float_or_none(result_data["odds"]),
                        "popularity": to_int_or_none(result_data["popularity"]),
                        "rank": to_int_or_none(result_data["rank"]),
                        "jockey_name": result_data["jockey_name"],
                        "weight_carried": result_data["weight_carried"],
                        "distance": result_data["distance"],
                        "ground_condition": result_data["ground_condition"],
                        "time": result_data["time"],
                        "margin": result_data["margin"],
                        "passing": result_data["passing"],
                        "pace": result_data["pace"],
                        "last_3f": result_data["last_3f"],
                        "body_weight": result_data["body_weight"],
                    },
                )
            return results
        except Exception as e:
            print(f"  -> 馬の成績取得エラー (ID: {horse_id}): {e}")
            return []


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


def main(race_id: str):
    analyzer = None
    try:
        analyzer = NetkeibaRaceAnalyzer()
        analyzer.get_race_entry(race_id)

        print("\n=== 処理完了 ===")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
    finally:
        if analyzer:
            analyzer.close()

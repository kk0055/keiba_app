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

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.db_base_url = "https://db.netkeiba.com"

    def close(self):
        if self.driver:
            self.driver.quit()

    def get_race_entries(self, race_id):
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
                pass
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "table[class*='RaceTable']")
                )
            )
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            entries = []
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

                # .get(index, default_value) のような安全な取得方法も良いが、ここではシンプルに
                waku = cells[0].text.strip() if len(cells) > 0 else ""
                umaban = cells[1].text.strip() if len(cells) > 1 else ""
                sex_age = cells[4].text.strip() if len(cells) > 4 else ""
                weight_carried = cells[5].text.strip() if len(cells) > 5 else ""
                jockey_name = cells[6].text.strip() if len(cells) > 6 else ""
                trainer_name = cells[7].text.strip() if len(cells) > 7 else ""
                horse_weight = cells[8].text.strip() if len(cells) > 8 else ""
                odds = cells[9].text.strip() if len(cells) > 9 else ""

                entry = {
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
                }
                entries.append(entry)
            # 馬番が確定している場合のみ、馬番でソートする
            if all(
                e.get("umaban", "").isdigit() and int(e["umaban"]) > 0 for e in entries
            ):
                print("-> 馬番が確定しているため、馬番順にソートします。")
                return sorted(entries, key=lambda x: int(x["umaban"]))
            else:
                print("-> 馬番が未確定のため、取得順のまま返します。")
                return entries

        except Exception as e:
            print(f"出馬表取得中にエラー: {e}")
            return []

    def get_horse_recent_results(self, horse_id, limit=10):

        if not horse_id:
            return []
        url = f"{self.db_base_url}/horse/{horse_id}/"
        time.sleep(1)
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
                    # "past_race_id": (
                    #     past_race_id_match.group(1) if past_race_id_match else ""
                    # ),
                    "head_count": cells[6].text.strip(),
                    "past_umaban": cells[7].text.strip(),
                    "past_waku": cells[8].text.strip(),
                    "past_odds": cells[9].text.strip(),
                    "popularity": cells[10].text.strip(),
                    "result_rank": cells[11].text.strip(),
                    "past_jockey_name": cells[12].text.strip(),
                    "past_weight_carried": cells[13].text.strip(),
                    "distance": cells[14].text.strip(),
                    "ground_condition": cells[15].text.strip(),
                    "time": cells[17].text.strip(),
                    "margin": cells[18].text.strip(),
                    "passing": cells[20].text.strip(),
                    "pace": cells[21].text.strip(),
                    "last_3f": cells[22].text.strip(),
                    "body_weight": cells[23].text.strip(),
                    # "prize_money": cells[27].text.strip().replace(",", ""),
                }
                results.append(result_data)
            return results
        except Exception as e:
            print(f"  -> 馬の成績取得エラー (ID: {horse_id}): {e}")
            return []

    def create_long_format_dataframe(self, entries, all_horse_results):
        """出走馬情報とその過去成績を縦に並べたデータフレームを作成する"""
        print("データを縦長フォーマットに整形しています...")

        combined_list = []
        for entry in entries:
            # 1. 出走情報を追加
            entry_row = entry.copy()
            entry_row["record_type"] = "出走情報"
            combined_list.append(entry_row)

            # 2. この馬の過去成績を抽出して追加
            horse_id = entry["horse_id"]
            past_races = [r for r in all_horse_results if r.get("horse_id") == horse_id]

            # 日付の降順（新しい順）でソート
            past_races_sorted = sorted(
                past_races, key=lambda x: x["date"], reverse=True
            )

            for race in past_races_sorted:
                race_row = race.copy()
                # 紐付けと可読性のために馬番と馬名を追加
                race_row["umaban"] = entry["umaban"]
                race_row["horse_name"] = entry["horse_name"]
                race_row["record_type"] = "過去成績"
                combined_list.append(race_row)

            # 3. 馬ごとの区切り行を追加
            separator = {"record_type": "---"}
            combined_list.append(separator)

        if not combined_list:
            return pd.DataFrame()

        df = pd.DataFrame(combined_list)

        COLUMN_MAP_JA = {
            "record_type": "レコード種別",
            "umaban": "馬番",
            "waku": "枠番",
            "horse_name": "馬名",
            "sex_age": "性齢",
            "weight_carried": "今回の斤量",
            "jockey_name": "今回の騎手",
            "trainer_name": "調教師",
            "horse_weight": "馬体重(増減)",
            "odds": "オッズ",
            # 過去成績
            "date": "日付",
            "venue": "開催",
            "weather": "天気",
            "race_name": "レース名",
            "head_count": "頭数",
            "past_umaban": "過去の馬番",
            "past_waku": "過去の枠番",
            "past_odds": "過去のオッズ",
            "result_rank": "着順",
            "past_jockey_name": "過去の騎手",
            "past_weight_carried": "過去の斤量",
            "distance": "コース",
            "ground_condition": "馬場状態",
            "time": "タイム",
            "margin": "着差",
            "passing": "通過",
            "pace": "ペース",
            "last_3f": "last_3f",
            # "prize_money": "賞金(円)",
            # "horse_id": "馬ID",
            # "past_race_id": "過去レースID",
            # "race_id": "現レースID",
        }

        # 2. 出力するカラムの順番を定義（自由に変更して）
        FINAL_COLUMN_ORDER = [
            # 基本情報
            "record_type",
            "umaban",
            "waku",
            "horse_name",
            "sex_age",
            "weight_carried",
            "jockey_name",
            "trainer_name",
            "horse_weight",
            "odds",
            # 過去成績
            "date",
            "venue",
            "weather",
            "race_name",
            "head_count",
            "past_umaban",
            "past_waku",
            "past_odds",
            "result_rank",
            "past_jockey_name",
            "past_weight_carried",
            "distance",
            "ground_condition",
            "time",
            "margin",
            "passing",
            "pace",
            "last_3f",
            "body_weight",
            # ID情報（最後）
            # "horse_id",
            # "past_race_id",
            # "race_id",
        ]
        # 存在しないカラムは無視し、存在するカラムだけをこの順番で並べる
        existing_columns_in_order = [
            col for col in FINAL_COLUMN_ORDER if col in df.columns
        ]
        df_ordered = df[existing_columns_in_order]
        # カラム名を日本語に変換
        df_final = df_ordered.rename(columns=COLUMN_MAP_JA)

        return df_final

    def analyze_and_format(self, race_id):
        """データ取得から整形までの一連の処理を実行する"""
        entries = self.get_race_entries(race_id)
        if not entries:
            print("出走馬が見つからなかったため、処理を終了します。")
            return None

        print(f"{len(entries)}頭の出走馬を取得。各馬の過去成績を取得します...")

        all_horse_results = []
        for i, entry in enumerate(entries, 1):
            print(
                f"[{i}/{len(entries)}] {entry['horse_name']} (ID: {entry['horse_id']})"
            )
            recent_results = self.get_horse_recent_results(entry["horse_id"])
            for result in recent_results:
                result["horse_id"] = entry["horse_id"]  # 紐付け用ID
                all_horse_results.append(result)

        long_format_df = self.create_long_format_dataframe(entries, all_horse_results)
        return long_format_df


def main():
    # --- CLI引数の設定 ---
    parser = argparse.ArgumentParser(
        description="netkeiba.comから指定されたrace_idの出馬表と過去成績を取得し、縦長のCSVファイルで出力します。",
        formatter_class=argparse.RawTextHelpFormatter,  # ヘルプメッセージの改行を保持
    )
    parser.add_argument(
        "race_id", help="取得したいレースのrace_id\n例: 202406030811 (2024年 皐月賞)"
    )
    args = parser.parse_args()
    race_id = args.race_id
    # --- ここまで ---

    analyzer = None
    try:
        analyzer = NetkeibaRaceAnalyzer()
        long_format_df = analyzer.analyze_and_format(race_id)

        if long_format_df is not None and not long_format_df.empty:
            output_dir = "race_data"
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.join(output_dir, f"long_format_summary_{race_id}.csv")
            long_format_df.to_csv(filename, index=False, encoding="utf-8-sig")

            print(f"\n見やすい縦長形式のCSVファイルが保存されました: {filename}")
            print("\n=== 処理完了 ===")
        else:
            print("\n=== 処理中断 ===")

    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
    finally:
        if analyzer:
            analyzer.close()


if __name__ == "__main__":
    main()

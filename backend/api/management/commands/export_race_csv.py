# racing_app/management/commands/export_race_csv.py

import csv  # csvライブラリをインポート
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, Count, Sum
from api.models import Race, Entry 
from api.serializers import (
    RaceSerializer,
    EntrySerializer,
)  
import os

class Command(BaseCommand):
    help = "指定されたrace_idのレース詳細データをCSVファイルとして出力します。"

    def add_arguments(self, parser):
        parser.add_argument("race_id", type=str, help="出力したいレースのrace_id")

    def handle(self, *args, **options):
        race_id = options["race_id"]
        self.stdout.write(f"race_id: {race_id} のCSVデータ出力を開始します...")

        race = Race.objects.filter(race_id=race_id).first()

        if not race:
            raise CommandError("データ取得後もレース情報が存在しません。")

        win_place_condition = Q(horse__past_races__rank__in=[1, 2, 3])

        sorted_entries = (
            Entry.objects.filter(race=race)
            .select_related("jockey", "horse")
            .prefetch_related("horse__past_races")
            .annotate(
                win_place_count=Count("horse__past_races", filter=win_place_condition),
                sum_grade_score=Sum("horse__past_races__race_grade_score"),
            )
            .order_by("-win_place_count", "-sum_grade_score")
        )

        race_serializer = RaceSerializer(race)
        entry_serializer = EntrySerializer(sorted_entries, many=True)

        response_data = race_serializer.data
        response_data["entries"] = entry_serializer.data

        # --- ファイルに出力 ---
        output_dir = os.path.join("output\CSVfiles")

        # 2. ディレクトリが存在しない場合は、安全に作成します
        os.makedirs(output_dir, exist_ok=True)

        # 3. ディレクトリのパスとCSVファイル名を結合して、書き込み先の「完全なパス」を生成します
        output_filename = os.path.join(output_dir, f"{race_id}.csv")

        header = [
            "レコード種別",
            "馬番",
            "枠番",
            "馬名",
            # "性齢",
            "今回の斤量",
            "今回の騎手",
            # "調教師",
            # "馬体重(増減)",
            "オッズ",
            "日付",
            "開催",
            "天気",
            "レース名",
            "頭数",
            "過去の馬番",
            "過去の枠番",
            "過去のオッズ",
            "着順",
            "過去の騎手",
            "過去の斤量",
            "コース",
            "馬場状態",
            "タイム",
            "着差",
            "通過",
            "ペース",
            "last_3f",
            "body_weight",
        ]

        try:
            with open(output_filename, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)

                # 1. ヘッダーを書き込む
                writer.writerow(header)

                # 2. シリアライズされたデータをループして行を作成
                for entry in response_data["entries"]:

                    # entry自体がNoneでないかチェック
                    if not entry:
                        self.stdout.write(self.style.WARNING(f"Entry #{i+1} is None or empty. Skipping."))
                        continue
                    horse_data = entry.get("horse") or {}
                    jockey_data = entry.get('jockey') or {} 

                    # --- 「出走情報」行を作成 ---
                    entry_row = [
                        "出走情報",
                        entry.get("umaban", ""),
                        entry.get("waku", ""),
                        horse_data.get("horse_name", ""),
                        # horse_data.get(
                        #     "sex_age", ""
                        # ),  
                        entry.get("weight_carried", ""),
             
                        jockey_data.get("jockey_name", ""),
                        # horse_data.get(
                        #     "trainer_name", ""
                        # ),  
                        # horse_data.get(
                        #     "horse_weight_display", ""
                        # ),  
                        entry.get("odds", ""),
                        # 以下、過去成績用のカラムは空欄
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                    writer.writerow(entry_row)

                    # --- 「過去成績」行をループで作成 ---
                    past_races = horse_data.get("past_races", [])

                    if past_races:  # リストが空やNoneでない場合のみ処理
                        for past_race in past_races:
                            # past_race自体がNoneの可能性をチェックし、スキップする
                            if not past_race:
                                continue 
                            past_race_row = [
                                "過去成績",
                                entry.get("umaban", ""),
                                "",
                                horse_data.get("horse_name", ""),
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",  # 出走情報用のカラムは空欄
                                past_race.get("race_date", ""),
                                past_race.get("venue_name", ""),
                                past_race.get("weather", ""),
                                past_race.get("race_name", ""),
                                past_race.get("head_count", ""),
                                past_race.get("umaban", ""),  # 過去のレースの馬番
                                past_race.get("waku", ""),  # 過去のレースの枠番
                                past_race.get("odds", ""),  # 過去のレースのオッズ
                                past_race.get("rank", ""),
                                past_race.get("jockey_name", ""),
                                past_race.get("weight_carried", ""),
                                past_race.get("distance", ""),
                                past_race.get("ground_condition", ""),
                                past_race.get("time", ""),
                                past_race.get("margin", ""),
                                past_race.get("passing", ""),
                                past_race.get("pace", ""),
                                past_race.get("last_3f", ""),
                                past_race.get("body_weight", ""),
                            ]
                            writer.writerow(past_race_row)

                    # --- 区切り行を書き込む ---
                    # ヘッダーの数に合わせて空の要素を追加
                    writer.writerow(["---"] + [""] * (len(header) - 1))

            self.stdout.write(
                self.style.SUCCESS(f"正常に '{output_filename}' を出力しました。")
            )

        except Exception as e:
            raise CommandError(f"ファイル出力中にエラーが発生しました: {str(e)}")

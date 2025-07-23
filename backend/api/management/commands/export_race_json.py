# racing_app/management/commands/export_race_json.py

import json
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, Count, Sum
from api.models import Race, Entry
from api.serializers import RaceSerializer, EntrySerializer
import os

# from racing_app.utils import scrape_and_save_race # 必要であればインポート


class Command(BaseCommand):
    help = "指定されたrace_idのレース詳細データをJSONファイルに出力します。"

    def add_arguments(self, parser):
        # コマンドラインから race_id を受け取るための引数を定義
        parser.add_argument("race_id", type=str, help="出力したいレースのrace_id")

    def handle(self, *args, **options):
        race_id = options["race_id"]
        self.stdout.write(f"race_id: {race_id} のデータ出力を開始します...")

        # --- RaceDetailViewのロジックをここに再現・再利用 ---
        race = Race.objects.filter(race_id=race_id).first()
        if not race:
            self.stdout.write(
                f"{race_id} がDBに存在しないため、データ取得を試みます..."
            )
            try:
                # scrape_and_save_race(race_id) # スクレイピングを実行
                self.stdout.write("データ取得が完了しました。")
                race = Race.objects.filter(race_id=race_id).first()
            except Exception as e:
                raise CommandError(f"データ取得に失敗しました: {str(e)}")

        if not race:
            raise CommandError(
                "データ取得後もレース情報が存在しません。処理を中断します。"
            )

        # --- Viewと同じクエリを実行 ---
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

        # --- Viewと同じシリアライズ処理 ---
        race_serializer = RaceSerializer(race)
        entry_serializer = EntrySerializer(sorted_entries, many=True)

        response_data = race_serializer.data
        response_data["entries"] = entry_serializer.data

        # --- ファイルに出力 ---
        output_dir = os.path.join( "JSONfiles")
        os.makedirs(output_dir, exist_ok=True)

        # ファイル名を含めた完全パス
        output_filename = os.path.join(output_dir, f"{race_id}.json")
        
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                # json.dump で整形して書き込み
                json.dump(response_data, f, ensure_ascii=False, indent=2)

            self.stdout.write(
                self.style.SUCCESS(f"正常に '{output_filename}' を出力しました。")
            )
        except Exception as e:
            raise CommandError(f"ファイル出力中にエラーが発生しました: {str(e)}")

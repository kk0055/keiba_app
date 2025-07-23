# backend/api/management/commands/run_race_pipeline.py

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "レース情報のスクレイピングとCSVエクスポートを順次実行します。"

    def add_arguments(self, parser):
        parser.add_argument("race_id", type=str, help="出力したいレースのrace_id")

    def handle(self, *args, **options):
        race_id = options["race_id"]
        self.stdout.write(self.style.SUCCESS("スクレイピングを開始します。"))

        # 1. scrape_race コマンドを実行
        try:
            self.stdout.write(self.style.SUCCESS("scrape_race コマンドを実行中..."))
            call_command(
                "scrape_race", race_id
            )  # ここで scrape_race.py のコマンド名を指定
            self.stdout.write(self.style.SUCCESS("scrape_race が正常に完了しました。"))
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"scrape_race コマンドの実行中にエラーが発生しました: {e}"
                )
            )
            return  # エラー時は後続処理を停止

        # 2. export_race_csv コマンドを実行
        try:
            self.stdout.write(self.style.SUCCESS("export_race_csv コマンドを実行中..."))
            call_command(
                "export_race_csv", race_id
            )  
            self.stdout.write(
                self.style.SUCCESS("export_race_csv が正常に完了しました。")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"export_race_csv コマンドの実行中にエラーが発生しました: {e}"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS("スクレイピングとCSVエクスポートが正常に完了しました。")
        )

from django.core.management import call_command

def scrape_and_save_race(race_id):
    """
    scrape_raceの呼び出し
    """
    try:
        call_command("scrape_race", race_id)
    except Exception as e:
        # 必要に応じて例外処理
        raise e

    pass

def export_race_csv(race_id):
    """
    export_race_csvの呼び出し
    """
    try:
        call_command("export_race_csv", race_id)
    except Exception as e:
        # 必要に応じて例外処理
        raise e

    pass


def scrape_and_export_csv(race_id):
    """
    scrape_race + export_race_csvの呼び出し
    """
    try:
        call_command("scrape_and_export_csv", race_id)
    except Exception as e:
        # 必要に応じて例外処理
        raise e

    pass

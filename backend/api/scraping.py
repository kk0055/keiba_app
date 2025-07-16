from django.core.management import call_command

def scrape_and_save_race(race_id):
    """
    race_idをもとにスクレイピングし、
    レース情報・Entryなど関連モデルへの登録処理
    - レース基本情報の取得・保存
    - 出走情報(Item)の取得・登録
    - JockeyやHorseなど関連モデルの作成 or 更新

    """
    try:
        call_command("scrape_race", race_id)
    except Exception as e:
        # 必要に応じて例外処理
        raise e
      
    pass

import argparse
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BatonScrape:
    """
    指定されたサイトにログインし、情報をスクレイピングするためのクラス。
    """

    def __init__(self, base_url: str):
        """WebDriverとオプションを初期化します。"""
        print("WebDriverを初期化しています...")
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        # options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        options.add_argument("--disable-gpu")
        options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )
        options.add_argument("--disable-popup-blocking")

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"WebDriverの初期化中にエラーが発生しました: {e}")
            raise

        self.base_url = base_url
        print("WebDriverの初期化が完了しました。")

    def close(self):
        """WebDriverを終了します。"""
        if self.driver:
            self.driver.quit()
            print("ブラウザを終了しました。")

    def login(self, email, password):
        """
        指定された認証情報を使用してサイトにログインします。
        """
        try:
            self.driver.get(self.base_url)

            # ユーザー名入力フィールドを待機して入力
            print("ユーザー名フィールドを待機中...")
            xpath_for_email = (
                "//dt[contains(., 'メールアドレス')]/following-sibling::dd[1]/input"
            )
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath_for_email))
            )
            email_field.clear()
            email_field.send_keys(email)
            print(f"メールアドレス「{email}」を入力しました。")

            # パスワード入力フィールドを特定して入力
            print("パスワード入力フィールドを待機中...")
            xpath_for_password = (
                "//dt[contains(., 'パスワード')]/following-sibling::dd[1]/input"
            )
            password_field = self.driver.find_element(By.XPATH, xpath_for_password)
            password_field.clear()
            password_field.send_keys(password)
            print("パスワードを入力しました。")

            # 3. 「ログイン」という表示のボタンを特定
            print("ログインボタンを待機中...")
            xpath_for_submit = "//input[@value='ログイン']"
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_for_submit))
            )
            submit_button.click()
            print("ログインボタンをクリックしました。")
            time.sleep(3)

            return True

        except TimeoutException:
            print(
                "ログイン処理中にタイムアウトしました。ID/パスワードが間違っているか、ページ構造が変更された可能性があります。"
            )
            # 失敗した時点のスクリーンショットを保存するとデバッグに役立ちます
            self.driver.save_screenshot("login_failed.png")
            print("スクリーンショット 'login_failed.png' を保存しました。")
            return False
        except Exception as e:
            print(f"ログイン処理中に予期せぬエラーが発生しました: {e}")
            return False

    def click_manager_link_and_switch_tab(self):
        """
        「LIFULL HOME'S Manager」のリンクをクリックし、新しいタブに移動します。
        """
        print("\n=== 新しいタブへの移動処理を開始 ===")
        try:
            # 1. クリック前のウィンドウハンドル（タブID）を記憶
            original_window = self.driver.current_window_handle

            # 2. 「LIFULL HOME'S Manager」のリンクを特定してクリック
            print("「LIFULL HOME'S Manager」のリンクを探しています...")
            xpath_for_manager_link = '//a[contains(., "LIFULL HOME\'S Manager")]'
            manager_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_for_manager_link))
            )
            manager_link.click()
            print("リンクをクリックしました。新しいタブが開くのを待ちます...")

            # 3. 新しいタブが開くまで待機 (最大10秒)
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            for window_handle in self.driver.window_handles:
                if window_handle != original_window:
                    self.driver.switch_to.window(window_handle)
                    break
            print("新しいタブに正常に移動しました。")
            return True
        except Exception as e:
            print(f"リンクのクリックまたはタブの切り替え中にエラーが発生しました: {e}")
            self.driver.save_screenshot("tab_switch_error.png")
            return False

    def click_property_list_link(self):
        """「取扱物件一覧」リンクをクリックしてページを移動します。"""
        print("\n=== 「取扱物件一覧」に移動します ===")
        try:
            xpath = "//a[text()='取扱物件一覧']"
            link = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            link.click()
            print("「取扱物件一覧」をクリックしました。")
            # 次のページに「編集」ボタンが表示されるまで待つ
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//a[text()='編集']"))
            )
            print("物件一覧ページに遷移しました。")
            return True
        except (TimeoutException, NoSuchElementException):
            print(
                "「取扱物件一覧」リンクが見つからないか、一覧ページの読み込みに失敗しました。"
            )
            self.driver.save_screenshot("property_list_error.png")
            return False

    def process_all_properties(self):
        """
        物件一覧ページにある全ての「編集」リンクを順番に処理します。
        """
        print("\n=== 全ての物件の処理を開始します ===")
        try:
            property_list_window = self.driver.current_window_handle

            edit_links = self.driver.find_elements(By.XPATH, "//a[text()='編集']")
            num_properties = len(edit_links)
            print(f"発見した物件数: {num_properties}")

            if num_properties == 0:
                print("編集対象の物件が見つかりませんでした。")
                return

            # 発見した物件の数だけループ処理
            for i in range(num_properties):
                print(f"\n--- {i + 1} / {num_properties} 件目の物件を処理中 ---")

                before_handles = set(self.driver.window_handles)
                print(f"クリック前のタブID: {before_handles}")

                all_edit_links = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//a[text()='編集']")
                    )
                )
                # all_edit_links = WebDriverWait(self.driver, 10).until(
                #     EC.presence_of_all_elements_located((By.XPATH, edit_links_xpath))
                # )

                target_link = all_edit_links[i]

                print(f"「編集」リンクのURLを取得: {target_link.get_attribute('href')}")
                print("リンクをクリックします...")
                target_link.click()

                # 新しいタブが開くまで待機 (10秒)
                WebDriverWait(self.driver, 10).until(
                    EC.number_of_windows_to_be(len(before_handles) + 1)
                )

                # クリック後のタブIDのリストを取得
                after_handles = set(self.driver.window_handles)
                print(f"クリック後のタブID: {after_handles}")

                # 新しいタブのIDを特定 (差分を取る)
                new_window_handle = list(after_handles - before_handles)[0]
                print(f"発見した新しいタブID: {new_window_handle}")

                # 新しいタブに移動する
                print("新しいタブに移動します...")
                self.driver.switch_to.window(new_window_handle)

                print("編集ページの読み込みを待機しています...")
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "tab-base-note"))
                )
                print("編集ページへの移動と読み込みが完了しました。")

                # 編集ページでの作業を実行
                if not self.scrape_edit_page():
                    print(
                        f"!!! {i+1}件目の物件処理に失敗したため、ループを中断します。"
                    )
                    return False  # 異常終了

                print("編集ページでの作業が完了したため、現在のタブを閉じます。")
                self.driver.close()  # 現在の（編集用）タブを閉じる

                print("物件一覧ページにフォーカスを戻します。")
                # 操作対象を物件一覧タブに（念のため）戻す
                self.driver.switch_to.window(property_list_window)
                print("物件一覧ページにフォーカスを戻しました。")

                time.sleep(1)  # 次のループに移る前に少し待機

            return True
        except Exception as e:
            print(f"!!! 物件処理のループ中に致命的なエラーが発生しました !!!")
            print(f"エラーの種類: {type(e).__name__}")
            print(f"エラーメッセージ: {e}")
            self.driver.save_screenshot("loop_processing_error.png")
            print(
                "エラー発生時のスクリーンショット 'loop_processing_error.png' を保存しました。"
            )
            return False  # 異常終了

    def scrape_edit_page(self):
        """
        編集ページで「備考」タブの情報を更新し、登録する一連の作業を行います。
        (最終手段：JavaScript関数を直接呼び出すバージョン)
        """
        print("--- [編集ページでの作業開始] ---")
        try:
            wait = WebDriverWait(self.driver, 20)

            # --- デバッグ用ステップ 1 ---
            print("デバッグ: ページ到着直後のスクリーンショットを撮ります...")
            self.driver.save_screenshot("debug_0_page_landed.png")

            # 1. 「備考」タブをクリックするのではなく、JavaScript関数を直接実行
            print(
                "ステップ1: JavaScript関数 'tabSwitch(\"note\")' を直接呼び出します..."
            )
            try:
                self.driver.execute_script("return tabSwitch('note');")
                print("JavaScript関数を実行しました。")
            except Exception as e:
                print(f"!!! 'tabSwitch'関数の実行に失敗しました: {e} !!!")
                # 失敗しても続行を試みる

            # --- デバッグ用ステップ 2 ---
            print("デバッグ: 関数実行直後のスクリーンショットを撮ります...")
            self.driver.save_screenshot("debug_1_after_js_call.png")

            # 2. テキストエリアが表示されるまで待機
            # これが成功すれば、タブ切り替えは成功している
            print("ステップ2: テキストエリアが表示されるのを待機します...")
            textarea = wait.until(EC.visibility_of_element_located((By.ID, "tokuchou")))
            print("テキストエリアの表示を確認しました。タブ切り替え成功です。")

            # 3. テキストエリアの文字の最後に「☆」を追加
            current_text = textarea.get_attribute("value")
            if not current_text.endswith("♪"):
                new_text = current_text[:-1] + "♪"
                textarea.clear()
                textarea.send_keys(new_text)
                print("テキストエリアに「☆」を追記しました。")
            else:
                print("テキストエリアには既に「☆」が追記済みのため、スキップします。")

            # 4. 「確認へ進む」ボタンをクリック
            print("ステップ3: 「確認へ進む」ボタンをクリックします...")
            confirm_button = wait.until(
                EC.element_to_be_clickable((By.ID, "submit_confirm_note"))
            )
            confirm_button.click()

            # 5. 「登録する」ボタンをクリック
            print("ステップ4: 「登録する」ボタンをクリックします...")
            register_button = wait.until(
                EC.element_to_be_clickable((By.ID, "reg_complete"))
            )
            register_button.click()

            # close_link = wait.until(
            #     EC.element_to_be_clickable((By.LINK_TEXT, "このページを閉じる"))
            # )
            # close_link.click()
            print("--- [編集ページでの作業完了] ---")
            return True

        except Exception as e:
            print(f"!!! 編集ページでの作業中に致命的なエラーが発生しました !!!")
            print(f"エラーの種類: {type(e).__name__}")
            print(f"エラーメッセージ: {e}")
            self.driver.save_screenshot("debug_2_error_occurred.png")
            print(
                "エラー発生時のスクリーンショット 'debug_2_error_occurred.png' を保存しました。"
            )

        print("--- [編集ページでの作業完了] ---")


def main():
    """
    スクレイピングを実行するメイン関数。
    """
    TARGET_BASE_URL = '',
    
    LOGIN_EMAIL = ""  # ログインユーザー名
    LOGIN_PASSWORD = "e"  # ログインパスワード

    scraper = None
    try:
        scraper = BatonScrape(base_url=TARGET_BASE_URL)

        if not scraper.login(LOGIN_EMAIL, LOGIN_PASSWORD):
            return  # ログイン失敗時はここで終了

        if not scraper.click_manager_link_and_switch_tab():
            return  # Managerタブへの移動失敗時はここで終了

        if not scraper.click_property_list_link():
            return  # 物件一覧への移動失敗時はここで終了

        # メインのループ処理を実行
        scraper.process_all_properties()

        print("\n=== 全ての処理が完了しました ===")

    except Exception as e:
        print(f"スクリプト全体で予期せぬエラーが発生しました: {e}")
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()

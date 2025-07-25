<!-- 不完全だしDocker使わずに起動できるようにしたいのでREADME2.mdを参照すること -->
# keiba_app
環境構築と起動方法

前提条件
Docker Desktopがインストールされていること
Windows / Macともに 公式サイトからインストールしてください

### Dockerイメージのビルド（初回またはDockerfile等の変更があった場合に実行）
```
docker-compose build
```
### Dockerコンテナの起動
```
docker-compose up -d
```
-d はバックグラウンド起動の意味です。
終了したい場合は docker-compose down を実行してください。
スクレイピングコマンドの実行方法
スクレイピングはDjangoコンテナ内で以下のコマンドを実行してください。

#### Djangoコンテナに入る(Dockerコンテナの中の環境に入るコマンド)
```
docker-compose exec backend /bin/bash
```

backendに移動
```
cd backend
```



スクレイピングコマンド実行例

python scrape_race <race_id>

例）
```
python scrape_race 202510020711
```
補足
Dockerを使うことで、Node.jsやPythonの環境をローカルに直接インストールしなくても動作します。



## 環境変数ファイルについて
環境変数を管理するために以下のファイルを使用。

.env
.env.local
.env

## ルート
ファイル名:.env
場所: keiba_app直下

役割
Dockerで使う環境変数を管理。


### フロントエンド (Next.js)
ファイル名: .env.local
場所: frontend直下

役割
Next.jsアプリの設定やAPIのエンドポイントなど、ローカル開発環境で使う環境変数を管理。


例
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_SOME_KEY=your_api_key_here

### バックエンド (Django)
ファイル名: .env
場所: backend直下

役割
Djangoの設定で使う秘密情報や接続設定（例: データベース接続情報、シークレットキーなど）を管理。Docker


例
SECRET_KEY=your_django_secret_key
DATABASE_URL=mysql://user:password@db_host:3306/db_name
DEBUG=True

使用方法
それぞれのディレクトリにファイルを作成してください。
具体的な値は別で共有


### エンドポイント
フロント
http://localhost:3000/

バックエンド
http://localhost:8000/




#### コンテナを停止
docker-compose down

#### イメージを再ビルド
docker-compose up --build
# keiba_app
環境構築と起動方法 (Dockerを使わない場合)

## 1. 前提条件
以下のツールが事前にインストールされている済

Python (3.10以上推奨): バックエンド用 (python3 --version)
Node.js (v18以上推奨): フロントエンド用 (node --version)
npm: フロントエンド用 (npm --version)
MySQL (v8.0推奨): データベース用 (MySQL Workbenchがあると便利)
MySQL Workbench
https://www.mysql.com/jp/products/workbench/

## 2. 環境構築

#### 事前にデータベースを作成
Workbenchを開いて下記コマンドでkeiba_appという名のDBを作成しておきます

```
CREATE DATABASE keiba_app CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
```

### ① バックエンド (Django)

バックエンドのディレクトリに移動します。
```
cd backend
```
仮想環境を作成
```
python3 -m venv venv
```

仮想環境を有効化（Mac/Linux の場合）
```
source venv/bin/activate
```
仮想環境を有効化（Windows の場合）
```
.\venv\Scripts\activate
```

必要なライブラリをインストール。
```
pip install -r requirements.txt
```

環境変数ファイルを作成します。.env.example をコピーして .env を作成
```
cp .env.example .env
```
その後、作成した .env ファイルをテキストエディタで開き、データベース情報を設定します。
.envに下記を追加してデータベース情報を設定

```
DB_ENGINE=django.db.backends.mysql
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

データベースのテーブルを作成
```
python manage.py migrate
```
ターミナルにマイグレーションが適用されるログが表示されれば成功


### ② フロントエンド (Next.js)

フロントエンドのディレクトリに移動します。
```
cd frontend
```
必要なライブラリをインストール

```
npm install
```

環境変数ファイルを作成します。frontendディレクトリ直下に .env.local という名前でファイルを作成し下記を追加してください。
 

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## アプリケーションの起動
フロントエンドとバックエンドは、それぞれ別のターミナルで起動する必要があります。

#### バックエンドの起動 (ターミナル1)
```
cd backend
source venv/bin/activate  # Windows: .\venv\Scripts\activate
python manage.py runserver
```
👉 バックエンドは http://localhost:8000 で起動します。

#### フロントエンドの起動 (ターミナル2)
```
cd frontend
npm run dev
```
👉 フロントエンドは http://localhost:3000 で起動します。
ブラウザで http://localhost:3000 にアクセスしてください。


## その他
#### ターミナルでのスクレイピングコマンド実行例
レースデータを取得するには、backendに移動後、バックエンドの仮想環境を有効化した状態で以下のコマンドを実行します。

使用法: python manage.py scrape_race <race_id>
例
```
python manage.py scrape_race 202510020711
```

CSV出力
```
python manage.py export_race_csv 202510020811 
```

スクレイピング+CSV出力
```
python manage.py scrape_and_export_csv 202510020811 
```

今回のレースのみ更新
```
python manage.py scrape_race 202510020811 --entry-only
```

### エンドポイント
フロント
http://localhost:3000/

バックエンド
http://localhost:8000/

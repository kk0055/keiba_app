# ベースイメージを指定
FROM node:14

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    --no-install-recommends

# Googleの公開鍵を追加
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

# Chromeのリポジトリを追加
RUN sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Google Chromeをインストール
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends

# node_modulesをインストール
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install

# アプリケーションのソースコードをコピー
COPY . .

# 環境変数設定（必要に応じて）
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_PATH=/usr/bin/google-chrome

# アプリケーションを起動
CMD ["yarn", "start"]
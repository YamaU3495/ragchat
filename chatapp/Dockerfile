# ビルドステージ
FROM node:20-alpine as build

WORKDIR /app

# 依存関係のインストール
COPY package*.json ./
RUN npm install

# ソースコードのコピー
COPY . .

# ビルド
RUN npm run build -- --mode production

# 本番ステージ
FROM --platform=linux/amd64 nginx:alpine

# 必要なツールをインストール
RUN apk add --no-cache bash

# Nginxの設定をコピー
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ビルドしたファイルをコピー
COPY --from=build /app/dist /usr/share/nginx/html

# 設定ファイルテンプレートをコピー
COPY public/config.template.js /usr/share/nginx/html/config.template.js

# 環境変数置換スクリプトをコピー
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# ポートの公開
EXPOSE 80

# エントリーポイントスクリプトを実行
ENTRYPOINT ["/docker-entrypoint.sh"] 
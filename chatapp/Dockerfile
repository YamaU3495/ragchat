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
FROM nginx:alpine

# Nginxの設定をコピー
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ビルドしたファイルをコピー
COPY --from=build /app/dist /usr/share/nginx/html

# ポートの公開
EXPOSE 80

# Nginxの起動
CMD ["nginx", "-g", "daemon off;"] 
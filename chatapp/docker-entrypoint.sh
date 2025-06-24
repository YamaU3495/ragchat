#!/bin/bash

# 環境変数のデフォルト値を設定
VITE_API_HOST=${VITE_API_HOST:-""}
VITE_API_PORT=${VITE_API_PORT:-""}
VITE_APP_TITLE=${VITE_APP_TITLE:-"LocalRAG Chat"}

echo "Configuring application with:"
echo "  VITE_API_HOST: $VITE_API_HOST"
echo "  VITE_API_PORT: $VITE_API_PORT"
echo "  VITE_APP_TITLE: $VITE_APP_TITLE"

# 設定ファイルテンプレートからconfig.jsを作成
sed -e "s|VITE_API_HOST_PLACEHOLDER|$VITE_API_HOST|g" \
    -e "s|VITE_API_PORT_PLACEHOLDER|$VITE_API_PORT|g" \
    -e "s|VITE_APP_TITLE_PLACEHOLDER|$VITE_APP_TITLE|g" \
    /usr/share/nginx/html/config.template.js > /usr/share/nginx/html/config.js

echo "Configuration file created: /usr/share/nginx/html/config.js"
echo "Configuration complete. Starting Nginx..."

# Nginxを起動
exec nginx -g "daemon off;" 
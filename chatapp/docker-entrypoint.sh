#!/bin/bash

set -e  # エラー時に終了

# 環境変数のデフォルト値を設定
VITE_API_HOST=${VITE_API_HOST:-""}
VITE_API_PORT=${VITE_API_PORT:-""}
VITE_APP_TITLE=${VITE_APP_TITLE:-"LocalRAG Chat"}

echo "=== Starting RAG Chat Frontend ==="
echo "Configuring application with:"
echo "  VITE_API_HOST: '$VITE_API_HOST'"
echo "  VITE_API_PORT: '$VITE_API_PORT'"
echo "  VITE_APP_TITLE: '$VITE_APP_TITLE'"

# 設定ファイルテンプレートの存在確認
if [ ! -f "/usr/share/nginx/html/config.template.js" ]; then
    echo "ERROR: config.template.js not found!"
    ls -la /usr/share/nginx/html/
    exit 1
fi

echo "Config template found. Creating config.js..."

# 設定ファイルテンプレートからconfig.jsを作成
# 空の値の場合は空文字列として扱う
sed -e "s|VITE_API_HOST_PLACEHOLDER|${VITE_API_HOST:-}|g" \
    -e "s|VITE_API_PORT_PLACEHOLDER|${VITE_API_PORT:-}|g" \
    -e "s|VITE_APP_TITLE_PLACEHOLDER|${VITE_APP_TITLE:-LocalRAG Chat}|g" \
    /usr/share/nginx/html/config.template.js > /usr/share/nginx/html/config.js

if [ $? -eq 0 ]; then
    echo "Configuration file created successfully: /usr/share/nginx/html/config.js"
    echo "Config file contents:"
    cat /usr/share/nginx/html/config.js
else
    echo "ERROR: Failed to create config.js"
    exit 1
fi

echo "Configuration complete. Starting Nginx..."

# Nginxの設定を確認
echo "Testing Nginx configuration:"
if nginx -t; then
    echo "Nginx configuration is valid"
else
    echo "ERROR: Nginx configuration is invalid"
    exit 1
fi

echo "=== Starting Nginx ==="
# Nginxを起動
exec nginx -g "daemon off;" 
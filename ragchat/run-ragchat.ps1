#!/usr/bin/env pwsh

# ragchat Docker起動スクリプト (PowerShell)
Write-Host "ragchat Dockerコンテナを起動します..." -ForegroundColor Green

# Dockerイメージ名
$IMAGE_NAME = "ragchat"

# コンテナ名
$CONTAINER_NAME = "ragchat-container"

# 既存のコンテナを停止・削除
Write-Host "既存のコンテナを確認・削除します..." -ForegroundColor Yellow
docker stop $CONTAINER_NAME 2>$null
docker rm $CONTAINER_NAME 2>$null

# appsettings.jsonの内容を環境変数として設定
Write-Host "環境変数を設定してコンテナを起動します..." -ForegroundColor Yellow

docker run -d `
  --name $CONTAINER_NAME `
  -p 80:80 `
  -e ASPNETCORE_ENVIRONMENT=Production `
  -e ASPNETCORE_URLS="http://+" `
  -e Logging__LogLevel__Default="Information" `
  -e Logging__LogLevel__Microsoft.AspNetCore="Warning" `
  -e AllowedHosts="*" `
  -e Api__Host="localhost" `
  -e Api__Port="8001" `
  -e Api__Protocol="http" `
  -e ChatService__Type="Api" `
  $IMAGE_NAME

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ ragchatコンテナが正常に起動しました!" -ForegroundColor Green
    Write-Host "アプリケーションURL: http://localhost" -ForegroundColor Cyan
    Write-Host "ログを確認: docker logs $CONTAINER_NAME" -ForegroundColor Cyan
    Write-Host "コンテナを停止: docker stop $CONTAINER_NAME" -ForegroundColor Cyan
} else {
    Write-Host "❌ コンテナの起動に失敗しました" -ForegroundColor Red
    Write-Host "エラーログを確認してください" -ForegroundColor Red
} 
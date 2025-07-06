# ragchat Docker起動スクリプト

appsettings.jsonの内容を環境変数として渡してragchatのDockerコンテナを起動するスクリプトです。

## 📁 ファイル構成

- `run-ragchat.ps1` - PowerShell版起動スクリプト
- `run-ragchat.sh` - bash版起動スクリプト
- `build-and-run.ps1` - ビルドから起動までの統合スクリプト（PowerShell）

## 🚀 使用方法

### 1. シンプルな起動（PowerShell）

```powershell
.\run-ragchat.ps1
```

### 2. シンプルな起動（bash）

```bash
./run-ragchat.sh
```

### 3. ビルドから起動まで（PowerShell）

```powershell
# デフォルト設定でビルド＋起動
.\build-and-run.ps1

# 設定を変更してビルド＋起動
.\build-and-run.ps1 -ApiHost "0.0.0.0" -ApiPort "8080"

# ビルドをスキップして起動のみ
.\build-and-run.ps1 -SkipBuild
```

### 4. 環境変数のカスタマイズ

```powershell
# 異なるAPI設定で起動
.\build-and-run.ps1 -ApiHost "api.example.com" -ApiPort "8080" -ApiProtocol "https"

# 異なるチャットサービスタイプで起動
.\build-and-run.ps1 -ChatServiceType "InMemory"
```

## ⚙️ 環境変数マッピング

appsettings.jsonの階層構造は以下のように環境変数にマッピングされます：

| appsettings.json | 環境変数 |
|------------------|----------|
| `Api:Host` | `Api__Host` |
| `Api:Port` | `Api__Port` |
| `Api:Protocol` | `Api__Protocol` |
| `ChatService:Type` | `ChatService__Type` |
| `Logging:LogLevel:Default` | `Logging__LogLevel__Default` |
| `Logging:LogLevel:Microsoft.AspNetCore` | `Logging__LogLevel__Microsoft.AspNetCore` |

## 🔧 設定されるデフォルト環境変数

```bash
# .NET Core環境設定
ASPNETCORE_ENVIRONMENT=Production
ASPNETCORE_URLS=http://+:8001

# ログレベル設定
Logging__LogLevel__Default=Information
Logging__LogLevel__Microsoft.AspNetCore=Warning

# ホスト設定
AllowedHosts=*

# API設定
Api__Host=localhost
Api__Port=8001
Api__Protocol=http

# チャットサービス設定
ChatService__Type=Api
```

## 📝 コンテナ操作

### ログの確認
```bash
docker logs ragchat-container
```

### コンテナの停止
```bash
docker stop ragchat-container
```

### コンテナの削除
```bash
docker rm ragchat-container
```

### イメージの削除
```bash
docker rmi ragchat
```

## 🐛 トラブルシューティング

### 1. ポートが使用中の場合
```powershell
# 異なるポートで起動
.\build-and-run.ps1 -ApiPort "8080"
```

### 2. コンテナが起動しない場合
```bash
# ログを確認
docker logs ragchat-container

# コンテナの状態を確認
docker ps -a
```

### 3. 権限エラーの場合（bash）
```bash
# 実行権限を付与
chmod +x run-ragchat.sh
```

## 🔄 更新手順

1. コードを更新
2. 既存のコンテナを停止・削除
3. 新しいイメージをビルド
4. コンテナを起動

```powershell
# すべてを一度に実行
.\build-and-run.ps1
```

## 📊 ヘルスチェック

`build-and-run.ps1`スクリプトは起動後に自動的にヘルスチェックを実行します。
アプリケーションが正常に動作しているかを確認できます。 
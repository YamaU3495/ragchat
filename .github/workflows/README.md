# GitHub Actions Workflows

このディレクトリには、RAGChatプロジェクトのGitHub Actionsワークフローが含まれています。

## ワークフロー一覧

### docker-build-push.yml
DockerイメージをビルドしてDockerHubにプッシュするワークフローです。

**トリガー方法:**
- GitHubのActionsタブから手動実行（workflow_dispatch）
- または、プルリクエストやプッシュ時に自動実行するように設定可能

**入力パラメータ:**
- `version`: Dockerイメージのバージョンタグ（デフォルト: latest）
- `push_to_registry`: DockerHubにプッシュするかどうか（デフォルト: true）

### update-azure-deployment.yml
Dockerイメージがプッシュされた後に、Azureデプロイメントスクリプトのイメージ名を自動更新するワークフローです。

**トリガー方法:**
- `docker-build-push.yml`ワークフローが成功した後に自動実行
- mainブランチでのみ実行

**機能:**
- Azureデプロイメントスクリプト（`deploy_to_azure/deploy/deploy.ps1`）のDockerイメージ名を自動更新
- 新しいバージョンのイメージ名でコミットとプッシュを実行

## 必要なGitHub Secrets

このワークフローを実行するには、以下のGitHub Secretsを設定する必要があります：

### 1. DOCKERHUB_USERNAME
DockerHubのユーザー名

### 2. DOCKERHUB_TOKEN
DockerHubのアクセストークン（パスワードではありません）

## GitHub Secretsの設定方法

### 1. DockerHubアクセストークンの作成
1. [DockerHub](https://hub.docker.com/)にログイン
2. 右上のユーザー名をクリック → "Account Settings"
3. 左サイドバーの"Security"をクリック
4. "New Access Token"をクリック
5. トークン名を入力（例: "GitHub Actions"）
6. トークンをコピーして保存（一度しか表示されません）

### 2. GitHub Secretsの設定
1. GitHubリポジトリのページで"Settings"タブをクリック
2. 左サイドバーの"Secrets and variables" → "Actions"をクリック
3. "New repository secret"をクリック
4. 以下の2つのシークレットを追加：

**DOCKERHUB_USERNAME**
- Name: `DOCKERHUB_USERNAME`
- Value: あなたのDockerHubユーザー名

**DOCKERHUB_TOKEN**
- Name: `DOCKERHUB_TOKEN`
- Value: 上記で作成したDockerHubアクセストークン

## ワークフローの実行方法

### 手動実行（推奨）
1. GitHubリポジトリの"Actions"タブをクリック
2. "Build and Push Docker Images"ワークフローを選択
3. "Run workflow"ボタンをクリック
4. 必要に応じてバージョンタグを変更
5. "Run workflow"をクリック

### 自動実行の設定
プルリクエストやプッシュ時に自動実行したい場合は、`docker-build-push.yml`の`on`セクションを以下のように変更：

```yaml
on:
  workflow_dispatch:
    # 手動実行の設定
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
```

## 出力されるDockerイメージ

ワークフローが成功すると、以下のDockerイメージが作成されます：

- `your-dockerhub-username/ragchat-frontend:latest`
- `your-dockerhub-username/ragchat-frontend:{version}`
- `your-dockerhub-username/ragchat-backend:latest`
- `your-dockerhub-username/ragchat-backend:{version}`

## トラブルシューティング

### よくある問題

1. **DockerHub認証エラー**
   - DOCKERHUB_USERNAMEとDOCKERHUB_TOKENが正しく設定されているか確認
   - アクセストークンが有効期限切れでないか確認

2. **ビルドエラー**
   - Dockerfileの構文エラーがないか確認
   - 依存関係ファイル（package.json, requirements.txt）が正しいか確認

3. **プッシュエラー**
   - DockerHubのレート制限に引っかかっていないか確認
   - イメージ名が重複していないか確認

### ログの確認方法
1. GitHubのActionsタブでワークフローを選択
2. 失敗したジョブをクリック
3. 失敗したステップをクリックしてログを確認 
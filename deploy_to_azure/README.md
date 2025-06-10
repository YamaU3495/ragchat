deploy_to_azureフォルダにAzureへのデプロイ用Bicepを作成します｡構成は以下のとおりです｡

### フォルダ構成
```
deploy_to_azure
├── init      # 初期化用のBicepファイル
├── deploy    # デプロイ用のBicepファイル
```

### init
環境初期化用のBicepファイルとスクリプトを作成します｡

#### デプロイするリソース
- Vnet
    - Subnet(プライベートエンドポイント用) <- PrivateSubnet
    - Subnet(ContainerEnvironment用)
    - Subnet(MongoDB用) <- PrivateSubnet
    - Subnet(Chromadb用) <- PrivateSubnet

#### デプロイ用のスクリプトの要件
- RGがなかったら作成する
- Bicepを利用してAzureリソースを作成する


### deploy
デプロイ用のBicepファイルとスクリプトを作成します｡

#### デプロイするリソース
- Container Apps Environment
    - Container Apps(frontend)
    - Container Apps(backend)
- MongoDB(VM)
- Chromadb(VM)

補足事項

- frontendとbackendは同一のContainerAppsEnvironmentに作成
- Container Apps　EnvironmentはInitで作成したSubnetに作成する｡
- Chromaは以下のTerraFormのテンプレートを参考にしてBicepのテンプレを作成して｡だだしVMの作成先はInitで作成したPrivateなSubnetとしPublicからのアクセスは不許可とします｡
  - 手順: https://docs.trychroma.com/production/cloud-providers/azure
  - テンプレ: https://github.com/chroma-core/chroma/blob/main/deployments/azure/main.tf
  - DockerCompose: https://s3.amazonaws.com/public.trychroma.com/cloudformation/assets/docker-compose.yml
- Mongodbは以下の手順を参考にUbuntuのVMにインストールしてください
  -  https://www.mongodb.com/ja-jp/docs/manual/tutorial/install-mongodb-on-ubuntu/
  - Versionは8.0.10とします｡


#### デプロイ用のスクリプトの要件
- デプロイ前にフロントエンドとバックエンドのDockerImageをDockerHubにPushする
- Bicepを実行する｡







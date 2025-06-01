# パラメータの設定
$resourceGroupName = "openai-rg"
$location = "japaneast"
$aiServiceName = "openai-service"
$customDomainName = "openai-service-domdom"
$modelDeploymentName = "gpt4-deployment"
$model = "gpt-4.1-mini"
$modelVersion = "2025-04-14"

# リソースグループの作成（存在しない場合）
$rgExists = az group exists --name $resourceGroupName
if ($rgExists -eq "false") {
    Write-Host "Creating resource group: $resourceGroupName"
    az group create --name $resourceGroupName --location $location
}

# Bicepのデプロイ
Write-Host "Deploying Bicep template..."
az deployment group create `
    --resource-group $resourceGroupName `
    --template-file main.bicep `
    --parameters `
        aiserviceaccountname=$aiServiceName `
        customDomainName=$customDomainName `
        modeldeploymentname=$modelDeploymentName `
        model=$model `
        modelversion=$modelVersion

# # デプロイ結果の確認
# Write-Host "Deployment completed. Checking status..."
# az deployment group show `
#     --resource-group $resourceGroupName `
#     --name main 
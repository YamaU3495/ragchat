param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$Location,
    
    [Parameter(Mandatory=$true)]
    [string]$AdminUsername,
    
    [Parameter(Mandatory=$false)]
    [string]$FrontendImage = "ragchat/ragchat-frontend:latest",
    
    [Parameter(Mandatory=$false)]
    [string]$BackendImage = "ragchat/ragchat-backend:latest",
    
    [Parameter(Mandatory=$false)]
    [int]$MaxRetries = 3,
    
    [Parameter(Mandatory=$false)]
    [int]$RetryDelaySeconds = 30
)

# Check if Azure CLI is installed
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI is not installed. Please install it first."
    exit 1
}

# Check if user is logged in
$account = az account show 2>$null
if (-not $?) {
    Write-Error "Please login to Azure first using 'az login'"
    exit 1
}

# SSH鍵の作成（存在しない場合のみ）
$SshKeyDir = "$HOME/.ssh"
$SshPrivateKeyPath = "$SshKeyDir/id_ragchat_rsa"
if (-not (Test-Path $SshPrivateKeyPath -PathType Leaf -ErrorAction SilentlyContinue)) {
    Write-Host "SSH鍵が存在しません。OpenSSLで新規作成します..."
    if (-not (Test-Path $SshKeyDir)) {
        New-Item -ItemType Directory -Path $SshKeyDir | Out-Null
    }
    & ssh-keygen -t rsa -b 4096 -f $HOME/.ssh/id_ragchat_rsa
    Write-Host "SSH鍵を作成しました: $SshPrivateKeyPath"
}

# Function to check for ongoing operations
function Wait-ForOngoingOperations {
    param (
        [string]$Location
    )
    
    $operations = az network operation list --location $Location --query "[?status=='InProgress']" -o json
    if ($operations -ne "[]") {
        Write-Host "Found ongoing operations. Waiting for them to complete..."
        while ($true) {
            $operations = az network operation list --location $Location --query "[?status=='InProgress']" -o json
            if ($operations -eq "[]") {
                break
            }
            Start-Sleep -Seconds 10
        }
    }
}

# Deploy the Bicep template with retry logic
$success = $false



Write-Host "Deploying Bicep template..."
az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file main.bicep `
    --parameters `
        resourceGroupName=$ResourceGroupName `
        location=$Location `
        frontendImage=$frontendImage `
        backendImage=$backendImage `
        adminUsername=$AdminUsername `
        sshPublicKey=$(cat "$($SshPrivateKeyPath).pub")

if ($LASTEXITCODE -eq 0) {
    $success = $true
} else {
    Write-Host "Deployment failed. Will retry in $RetryDelaySeconds seconds..."
    exit 1
}

if (-not $success) {
    Write-Error "Deployment failed after $MaxRetries attempts"
    exit 1
}

# Get the frontend URL
$frontendUrl = (az deployment group show `
    --resource-group $ResourceGroupName `
    --name main `
    --query properties.outputs.frontendUrl.value `
    --output tsv)

Write-Host "Deployment completed successfully!"
Write-Host "Frontend URL: $frontendUrl"

# Get MongoDB and ChromaDB private IPs
$mongodbIP = (az deployment group show `
    --resource-group $ResourceGroupName `
    --name main `
    --query properties.outputs.mongodbPrivateIP.value `
    --output tsv)

$chromaIP = (az deployment group show `
    --resource-group $ResourceGroupName `
    --name main `
    --query properties.outputs.chromaPrivateIP.value `
    --output tsv)

Write-Host "MongoDB Private IP: $mongodbIP"
Write-Host "ChromaDB Private IP: $chromaIP" 
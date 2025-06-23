param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [string]$Location='japaneast'
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

# Check if resource group exists, if not create it
$rgExists = az group exists --name $ResourceGroupName
if ($rgExists -eq "false") {
    Write-Host "Creating resource group $ResourceGroupName in $Location..."
    az group create --name $ResourceGroupName --location $Location
}

# Deploy the Bicep template
Write-Host "Deploying Bicep template..."
az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file main.bicep

if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployment failed"
    exit 1
}

Write-Host "Deployment completed successfully!" 
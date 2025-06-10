param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$Location,
    
    [Parameter(Mandatory=$true)]
    [string]$DockerHubUsername,
    
    [Parameter(Mandatory=$true)]
    [string]$DockerHubPassword,
    
    [Parameter(Mandatory=$true)]
    [string]$AdminUsername,
    
    [Parameter(Mandatory=$true)]
    [string]$AdminPassword,
    
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

# Login to Docker Hub
Write-Host "Logging in to Docker Hub..."
docker login -u $DockerHubUsername -p $DockerHubPassword
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to login to Docker Hub"
    exit 1
}

# Build and push frontend image
Write-Host "Building and pushing frontend image..."
$frontendImage = "${DockerHubUsername}/ragchat-frontend:latest"
docker build -t $frontendImage ../frontend
docker push $frontendImage
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to build and push frontend image"
    exit 1
}

# Build and push backend image
Write-Host "Building and pushing backend image..."
$backendImage = "${DockerHubUsername}/ragchat-backend:latest"
docker build -t $backendImage ../backend
docker push $backendImage
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to build and push backend image"
    exit 1
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
$retryCount = 0
$success = $false

while (-not $success -and $retryCount -lt $MaxRetries) {
    if ($retryCount -gt 0) {
        Write-Host "Retry attempt $retryCount of $MaxRetries..."
        Wait-ForOngoingOperations -Location $Location
        Start-Sleep -Seconds $RetryDelaySeconds
    }

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
            adminPassword=$AdminPassword

    if ($LASTEXITCODE -eq 0) {
        $success = $true
    } else {
        $retryCount++
        if ($retryCount -lt $MaxRetries) {
            Write-Host "Deployment failed. Will retry in $RetryDelaySeconds seconds..."
        }
    }
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
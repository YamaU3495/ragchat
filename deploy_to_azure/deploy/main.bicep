@description('The name of the resource group')
param resourceGroupName string

@description('The location for all resources')
param location string = resourceGroup().location

@description('The name of the virtual network')
param vnetName string = 'ragchat-vnet'

@description('The name of the container apps subnet')
param containerAppsSubnetName string = 'container-apps-subnet'

@description('The name of the MongoDB subnet')
param mongoDBSubnetName string = 'mongodb-subnet'

@description('The name of the ChromaDB subnet')
param chromaDBSubnetName string = 'chromadb-subnet'

@description('The Docker image for the frontend')
param frontendImage string

@description('The Docker image for the backend')
param backendImage string

@description('The admin username for VMs')
param adminUsername string

@description('The version of Chroma to install')
param chromaVersion string = '1.0.13'

@description('The SSH public key for the VM')
param sshPublicKey string

// Container Apps Environment
resource containerAppsEnv 'Microsoft.App/managedEnvironments@2025-02-02-preview' = {
  name: 'ragchat-env'
  location: location
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, containerAppsSubnetName)
      internal: false
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
    zoneRedundant: false
  }
}

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2025-02-01' = {
  name: 'ragchat-logs-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Frontend Container App
resource frontendApp 'Microsoft.App/containerApps@2025-02-02-preview' = {
  name: 'ragchat-frontend'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 3000
        transport: 'http'
        allowInsecure: false
      }
      secrets: []
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: frontendImage
          env: [
            {
              name: 'BACKEND_URL'
              value: 'http://ragchat-backend'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
}

// Backend Container App
resource backendApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'ragchat-backend'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: false
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
      }
      secrets: []
      registries: []
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: backendImage
          // env: [
          //   {
          //     name: 'MONGODB_URI'
          //     value: 'mongodb://${mongodbVM.properties.networkProfile.networkInterfaces[0].properties.privateIPAddress}:27017'
          //   }
          //   {
          //     name: 'CHROMA_URL'
          //     value: 'http://${chromaVM.properties.networkProfile.networkInterfaces[0].properties.privateIPAddress}:8000'
          //   }
          // ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }  
}

module chromaModule 'chroma.bicep' = {
  name: 'chromaModule'
  params: {
    location: location
    vnetName: vnetName
    chromaDBSubnetName: chromaDBSubnetName
    adminUsername: adminUsername
    sshPublicKey: sshPublicKey
    chromaVersion: chromaVersion
  }
}

// Outputs
// output frontendUrl string = frontendApp.properties.configuration.ingress.fqdn
// output mongodbPrivateIP string = mongodbVM.properties.networkProfile.networkInterfaces[0].properties.privateIPAddress
output chromaPrivateIP string = chromaModule.outputs.chromaPrivateIP 

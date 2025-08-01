@description('The name of the resource group')
param resourceGroupName string

@description('The location for all resources')
param location string = resourceGroup().location

@description('The name of the virtual network')
param vnetName string = 'ragchat-vnet'

@description('The name of the container apps subnet')
param containerAppsSubnetName string = 'container-apps-subnet'

@description('The address prefix for the container apps subnet')
param containerAppsSubnetPrefix string = '10.0.0.0/23'

@description('The name of the MongoDB subnet')
param mongoDBSubnetName string = 'mongodb-subnet'

@secure()
@description('The password for MongoDB')
param mongodbPassword string

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

@secure()
@description('The Azure OpenAI API Key')
param azureOpenAIApiKey string

@secure()
@description('The Azure Embedding Endpoint')
param azureEmbeddingEndpoint string

@secure()
@description('The Azure OpenAI Endpoint')
param azureOpenAIEndpoint string

@secure()
@description('The Keycloak client secret')
param keycloakClientSecret string

@description('The Keycloak authority')
param keycloakAuthority string

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
        targetPort: 8001
        transport: 'http'
        allowInsecure: false
      }
      secrets: [
        {
          name: 'keycloak-client-secret'
          value: keycloakClientSecret
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: frontendImage
          env: [
            { 
              name: 'ASPNETCORE_ENVIRONMENT'
              value: 'Production'
            }
            { 
              name: 'ASPNETCORE_URLS'
              value: 'http://+:8001'
            }
            { 
              name: 'Logging__LogLevel__Default'
              value: 'Information'
            }
            { 
              name: 'Logging__LogLevel__Microsoft__AspNetCore'
              value: 'Warning'
            }
            { 
              name: 'AllowedHosts'
              value: '*'
            }
            { 
              name: 'Api__Host'
              value: 'ragchat-backend'
            }
            { 
              name: 'Api__Port'
              value: '80'
            }
            { 
              name: 'Api__Protocol'
              value: 'http'
            }
            { 
              name: 'ChatService__Type'
              value: 'Api'
            }
            {
              name: 'Authentication__Schemes__KeycloakOidc__ClientSecret'
              secretRef: 'keycloak-client-secret'
            }
            {
              name: 'Authentication__Schemes__KeycloakOidc__Authority'
              value: keycloakAuthority
            }
            { 
              name: 'ASPNETCORE_FORWARDEDHEADERS_ENABLED'
              value: 'true'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }
}

// Backend Container App
resource backendApp 'Microsoft.App/containerApps@2025-02-02-preview' = {
  name: 'ragchat-backend'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: false
        targetPort: 8001
        transport: 'http'
        allowInsecure: true
      }
      secrets: [
        {
          name: 'azure-openai-endpoint'
          value: azureOpenAIEndpoint
        }
        {
          name: 'azure-openai-api-key'
          value: azureOpenAIApiKey
        }
        {
          name: 'azure-embedding-endpoint'
          value: azureEmbeddingEndpoint
        }
        {
          name: 'mongodb-password'
          value: mongodbPassword
        }
      ]
      registries: []
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: backendImage
          env: [
            {
              name: 'CHROMA_HOST'
              value: chromaModule.outputs.chromaPrivateIP
            }
            {
              name: 'CHROMA_PORT'
              value: '8000'
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              secretRef: 'azure-openai-endpoint'
            }
            {
              name: 'AZURE_OPENAI_API_KEY'
              secretRef: 'azure-openai-api-key'
            }
            {
              name: 'AZURE_EMBEDDING_ENDPOINT'
              secretRef: 'azure-embedding-endpoint'
            }
            {
              name: 'MONGODB_HOST'
              value: chromaModule.outputs.chromaPrivateIP
            }
            {
              name: 'MONGODB_PORT'
              value: '27017'
            }
            {
              name: 'MONGODB_USER'
              value: 'root'
            }
            {
              name: 'MONGODB_PASSWORD'
              secretRef: 'mongodb-password'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
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
    containerAppsSubnetPrefix: containerAppsSubnetPrefix
  }
}

// Outputs
// output frontendUrl string = frontendApp.properties.configuration.ingress.fqdn
// output mongodbPrivateIP string = mongodbVM.properties.networkProfile.networkInterfaces[0].properties.privateIPAddress
output chromaPrivateIP string = chromaModule.outputs.chromaPrivateIP 

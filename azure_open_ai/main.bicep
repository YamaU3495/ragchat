@description('This is the name of your AI Service Account')
param aiserviceaccountname string

@description('Custom domain name for the endpoint')
param customDomainName string

@description('Name of the deployment ')
param modeldeploymentname string

@allowed([
  'gpt-4.1-mini'
])
@description('The model being deployed. https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models?tabs=global-standard%2Cstandard-chat-completions')
param model string = 'gpt-4.1-mini'

@description('Version of the model being deployed')
param modelversion string = '2025-04-14'

@description('Capacity for specific model used')
param capacity int = 10

@description('Location for all resources.')
param location string = resourceGroup().location

@allowed([
  'S0'
])
param sku string = 'S0'

resource openAIService 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: aiserviceaccountname
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: sku
  }
  kind: 'AIServices'
  properties: {
    customSubDomainName: customDomainName
  }
}

resource azopenaideployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
    parent: openAIService
    name: modeldeploymentname
    properties: {
        model: {
            format: 'OpenAI'
            name: model
            version: modelversion
        }
    }
    sku: {
      name: 'GlobalStandard'
      capacity: capacity
    }
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
    parent: openAIService
    name: 'embedding-deployment'
    properties: {
        model: {
            format: 'OpenAI'
            name: 'text-embedding-3-large'
            version: '1'
        }
    }
    sku: {
      name: 'GlobalStandard'
      capacity: 120
    }
}


output openAIServiceEndpoint string = openAIService.properties.endpoint

@description('Azure region for resources')
param location string = resourceGroup().location

@description('OpenAI deployment model')
param openAIModel string = 'gpt-4o'

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'examnotes${uniqueString(resourceGroup().id)}'
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}

// Blob Containers
resource contentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/contents'
}

resource chunksContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/chunks'
}

resource outputContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/output'
}

// Azure OpenAI
resource openAI 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' = {
  name: 'examnotes-openai'
  location: location
  kind: 'OpenAI'
  sku: { name: 'S0' }
  properties: {
    customSubDomainName: 'examnotes-openai-${uniqueString(resourceGroup().id)}'
  }
}

// Azure Language Service
resource languageService 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' = {
  name: 'examnotes-language'
  location: location
  kind: 'TextAnalytics'
  sku: { name: 'S' }
}

// Function App (Durable Functions)
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: 'examnotes-func-${uniqueString(resourceGroup().id)}'
  location: location
  kind: 'functionapp'
  properties: {
    siteConfig: {
      appSettings: [
        { name: 'AZURE_OPENAI_ENDPOINT', value: openAI.properties.endpoint }
        { name: 'AZURE_LANGUAGE_ENDPOINT', value: languageService.properties.endpoint }
        { name: 'STORAGE_CONNECTION', value: storageAccount.properties.primaryEndpoints.blob }
      ]
    }
  }
}
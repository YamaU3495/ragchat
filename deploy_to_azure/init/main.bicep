@description('The location for all resources')
param location string = 'japaneast'

@description('The name of the virtual network')
param vnetName string = 'ragchat-vnet'

@description('The address space for the virtual network')
param vnetAddressSpace string = '10.0.0.0/16'

@description('The address prefix for the container apps subnet')
param containerAppsSubnetPrefix string = '10.0.0.0/23'

@description('The address prefix for the MongoDB subnet')
param mongoDBSubnetPrefix string = '10.0.4.0/23'

@description('The address prefix for the ChromaDB subnet')
param chromaDBSubnetPrefix string = '10.0.8.0/23'

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2023-04-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressSpace
      ]
    }
  }
}

// Container Apps Subnet
resource containerAppsSubnet 'Microsoft.Network/virtualNetworks/subnets@2024-05-01'  = {
  parent: vnet
  name: 'container-apps-subnet'
  properties: {
    addressPrefix: containerAppsSubnetPrefix
  }
}

// MongoDB Subnet
resource mongoDBSubnet 'Microsoft.Network/virtualNetworks/subnets@2024-05-01'  = {
  parent: vnet
  name: 'mongodb-subnet'
  properties: {
    addressPrefix: mongoDBSubnetPrefix
    defaultOutboundAccess: false
  }
}

// ChromaDB Subnet
resource chromaDBSubnet 'Microsoft.Network/virtualNetworks/subnets@2024-05-01'  = {
  parent: vnet
  name: 'chromadb-subnet'
  properties: {
    addressPrefix: chromaDBSubnetPrefix
    defaultOutboundAccess: false
  }
}

// Outputs
output vnetName string = vnet.name
output containerAppsSubnetName string = containerAppsSubnet.name
output mongoDBSubnetName string = mongoDBSubnet.name
output chromaDBSubnetName string = chromaDBSubnet.name 

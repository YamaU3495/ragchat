@description('The location for all resources')
param location string

@description('The name of the virtual network')
param vnetName string

@description('The name of the ChromaDB subnet')
param chromaDBSubnetName string

@description('The admin username for VMs')
param adminUsername string

@description('The SSH public key for the VM')
param sshPublicKey string

@description('The version of Chroma to install')
param chromaVersion string = '1.0.13'

resource chromaNIC 'Microsoft.Network/networkInterfaces@2023-04-01' = {
  name: 'chroma-nic'
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          privateIPAllocationMethod: 'Dynamic'
          subnet: {
            id: resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, chromaDBSubnetName)
          }
        }
      }
    ]
  }
}

resource chromaVM 'Microsoft.Compute/virtualMachines@2024-11-01' = {
  name: 'ragchat-chroma'
  location: location
  properties: {
    hardwareProfile: {
      vmSize: 'Standard_B1ms'
    }
    osProfile: {
      computerName: 'chroma'
      adminUsername: adminUsername
      linuxConfiguration: {
        disablePasswordAuthentication: true
        ssh: {
          publicKeys: [
            {
              path: '/home/${adminUsername}/.ssh/authorized_keys'
              keyData: sshPublicKey
            }
          ]
        }
      }
      customData: base64('''#!/bin/bash
USER=chroma
useradd -m -s /bin/bash $USER
apt-get update
apt-get install -y docker.io
usermod -aG docker $USER
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
systemctl enable docker
systemctl start docker
mkdir -p /home/$USER/config
cat <<'EOF' > /home/$USER/docker-compose.yml
version: '3.9'

networks:
  net:
    driver: bridge

services:
  server:
    image: ghcr.io/chroma-core/chroma:${chromaVersion}
    volumes:
      - ./chroma_data:/data
    ports:
      - "8000:8000"
    networks:
      - net
    environment:
      - ANONYMIZED_TELEMETRY=False

EOF
chown $USER:$USER /home/$USER/docker-compose.yml
cd /home/$USER
sudo -u $USER docker-compose up -d
''')
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: chromaNIC.id
        }
      ]
    }
    storageProfile: {
      imageReference: {
        publisher: 'Canonical'
        offer: 'ubuntu-24_04-lts'
        sku: 'server'
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
        managedDisk: {
          storageAccountType: 'Standard_LRS'
        }
        diskSizeGB: 128
      }
    }
  }
}

output chromaPrivateIP string = chromaNIC.properties.ipConfigurations[0].properties.privateIPAddress 
output chromaPort string = '8000'

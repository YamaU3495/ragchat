@description('すべてのリソースの場所 - 有効なAzureリージョンを指定してください')
param location string

@description('Chroma VMをデプロイする既存の仮想ネットワーク名')
param vnetName string

@description('ChromaDBデプロイ用の仮想ネットワーク内の既存サブネット名')
param chromaDBSubnetName string

@description('Chroma VMの管理者ユーザー名 - SSH接続に使用')
param adminUsername string

@description('VMのSSH公開鍵 - 安全な認証に使用（OpenSSH形式）')
param sshPublicKey string

@description('インストールするChroma Dockerイメージのバージョン - https://hub.docker.com/r/chromadb/chroma/tags を参照')
param chromaVersion string = '1.0.13'

// Chroma VM用のネットワークセキュリティグループ
// SSH（22番ポート）とChroma（8000番ポート）への外部アクセスを許可
resource chromaNSG 'Microsoft.Network/networkSecurityGroups@2024-07-01' = {
  name: 'chroma-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'AllowSSH'
        properties: {
          description: 'SSH接続をすべてのIP範囲から許可'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '22'
          sourceAddressPrefix: '*'          // すべてのIPアドレスから接続を許可
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 1000
          direction: 'Inbound'
        }
      }
      {
        name: 'AllowChroma'
        properties: {
          description: 'Chromaサービス（8000番ポート）への接続を許可'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '8000'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 1100
          direction: 'Inbound'
        }
      }
    ]
  }
}

// Chroma VM用のパブリックIPアドレスリソース
// 参考: https://learn.microsoft.com/ja-jp/azure/templates/microsoft.network/publicipaddresses
resource chromaPublicIP 'Microsoft.Network/publicIPAddresses@2024-07-01'  = {
  name: 'chroma-public-ip'  // リソース名 - リソースグループ内で一意である必要があります
  location: location        // リソースの場所 - リソースグループと同じ場所
  properties: {
    // パブリックIPアドレスの割り当て方法
    // 'Static' = 作成時に固定IPアドレスを割り当て（本番環境推奨）
    // 'Dynamic' = 関連リソース開始時にIPアドレスを割り当て
    publicIPAllocationMethod: 'Static'
    
    // パブリックIPアドレスのバージョン
    // 'IPv4' = 標準的なIPv4アドレス（最も一般的）
    // 'IPv6' = IPv6アドレス（デュアルスタックシナリオ用）
    publicIPAddressVersion: 'IPv4'
  }
  sku: {
    // パブリックIPアドレスのSKU名
    // 'Basic' = 基本SKU（機能制限あり、ゾーン冗長なし）
    // 'Standard' = 標準SKU（拡張機能、ゾーン冗長サポート、静的割り当てのみ）
    // 'StandardV2' = 追加機能を持つ最新バージョン
    name: 'Standard'
  }
}

// Chroma VM用のネットワークインターフェースリソース
// 参考: https://learn.microsoft.com/ja-jp/azure/templates/microsoft.network/2024-07-01/networkinterfaces
resource chromaNIC 'Microsoft.Network/networkInterfaces@2024-07-01' = {
  name: 'chroma-nic'     // リソース名 - リソースグループ内で一意である必要があります
  location: location     // リソースの場所 - リソースグループと同じ場所
  properties: {
    // ネットワークセキュリティグループの関連付け
    // SSH（22番）とChroma（8000番）ポートへのアクセスを制御
    networkSecurityGroup: {
      id: chromaNSG.id
    }
    // ネットワークインターフェースのIP設定のリスト
    // 各NICには少なくとも1つのIP設定が必要です
    ipConfigurations: [
      {
        name: 'ipconfig1'  // IP設定の名前 - NIC内で一意
        properties: {
          // プライベートIPアドレスの割り当て方法
          // 'Dynamic' = Azureがサブネット範囲から利用可能なIPを自動割り当て
          // 'Static' = プライベートIPアドレスを手動指定（サブネット範囲内である必要があります）
          privateIPAllocationMethod: 'Dynamic'
          
          // このNICが配置されるサブネットへの参照
          // NICはこのサブネットのアドレス範囲からIPアドレスを受け取ります
          subnet: {
            id: resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, chromaDBSubnetName)
          }
          
          // パブリックIPアドレスリソースへの参照
          // パブリックIPをこのネットワークインターフェースに関連付けます
          // このパブリックIPを通じてVMへの外部接続を可能にします
          publicIPAddress: {
            id: chromaPublicIP.id
          }
        }
      }
    ]
  }
}

// Chromaデータベース実行用の仮想マシンリソース
// 参考: https://learn.microsoft.com/en-us/azure/templates/microsoft.compute/2024-11-01/virtualmachines
resource chromaVM 'Microsoft.Compute/virtualMachines@2024-11-01' = {
  name: 'ragchat-chroma'  // VM名 - リソースグループ内で一意である必要があります
  location: location      // VMの場所 - リソースグループと同じ場所
  properties: {
    // VMのハードウェア構成
    hardwareProfile: {
      vmSize: 'Standard_B1ms'  // VMサイズ - 1 vCPU、2GB RAM、軽量ワークロードに適している
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
      customData: base64(format('''#!/bin/bash
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
    image: ghcr.io/chroma-core/chroma:{0}
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
''', chromaVersion))
    }
    // ネットワーク設定 - VMをネットワークインターフェースに接続
    networkProfile: {
      networkInterfaces: [
        {
          id: chromaNIC.id  // 上記で作成されたネットワークインターフェースへの参照
        }
      ]
    }
    // VMのストレージ設定
    storageProfile: {
      // OSイメージ設定 - Ubuntu 24.04 LTS Server
      imageReference: {
        publisher: 'Canonical'      // イメージ発行者
        offer: 'ubuntu-24_04-lts'   // Ubuntu 24.04 LTS
        sku: 'server'               // サーバーエディション（GUI なし）
        version: 'latest'           // 利用可能な最新バージョン
      }
      // OSディスク設定
      osDisk: {
        createOption: 'FromImage'   // イメージからディスクを作成
        managedDisk: {
          storageAccountType: 'Standard_LRS'  // 標準ローカル冗長ストレージ
        }
        diskSizeGB: 128             // OSディスクサイズ - OSとDockerコンテナ用に128GB
      }
    }
  }
}

// ネットワークインターフェースに割り当てられたプライベートIPアドレスを出力
// このIPは仮想ネットワーク内でのみアクセス可能です
output chromaPrivateIP string = chromaNIC.properties.ipConfigurations[0].properties.privateIPAddress 

// パブリックIPリソースに割り当てられたパブリックIPアドレスを出力
// このIPはインターネットからアクセス可能で、Chromaサービスへの接続に使用できます
output chromaPublicIP string = chromaPublicIP.properties.ipAddress

// Chromaサービスが動作するポート番号を出力
// chromaPublicIPと組み合わせて完全なエンドポイントを構成: http://<chromaPublicIP>:8000
output chromaPort string = '8000'

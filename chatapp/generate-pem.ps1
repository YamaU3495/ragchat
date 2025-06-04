# 秘密鍵を作成
openssl genrsa -out chatapp-key.pem 2048

# 証明書署名要求(CSR)を作成
openssl req -new -key chatapp-key.pem -out chatapp.csr `
  -subj "/C=JP/ST=Tokyo/L=Chiyoda/O=LocalDev/OU=Dev/CN=chatapp"

# 自己署名証明書を作成（有効期限365日）
openssl x509 -req -in chatapp.csr -signkey chatapp-key.pem -out chatapp-cert.pem -days 365
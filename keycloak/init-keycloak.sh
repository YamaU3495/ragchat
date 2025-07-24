#!/bin/bash

# Wait for Keycloak to be ready
echo "Waiting for Keycloak to be ready..."
until curl -s http://localhost:8080/health/ready; do
    echo "Keycloak is not ready yet. Waiting..."
    sleep 5
done

echo "Keycloak is ready. Getting admin token..."

# Get admin token
ADMIN_TOKEN=$(curl -s -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin" \
    -d "password=admin" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" \
    http://localhost:8080/realms/master/protocol/openid-connect/token | jq -r '.access_token')

if [ "$ADMIN_TOKEN" = "null" ] || [ -z "$ADMIN_TOKEN" ]; then
    echo "Failed to get admin token"
    exit 1
fi

echo "Admin token obtained. Creating realm..."

# Create realm
curl -s -X POST \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "realm": "ragchat",
        "enabled": true,
        "displayName": "RAG Chat",
        "displayNameHtml": "<div class=\"kc-logo-text\"><span>RAG Chat</span></div>"
    }' \
    http://localhost:8080/admin/realms

echo "Realm created. Creating client..."

# Create client
curl -s -X POST \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "ragchat",
        "enabled": true,
        "publicClient": false,
        "standardFlowEnabled": true,
        "directAccessGrantsEnabled": true,
        "serviceAccountsEnabled": true,
        "redirectUris": ["http://localhost/*", "http://frontend/*"],
        "webOrigins": ["http://localhost", "http://frontend"],
        "clientAuthenticatorType": "client-secret",
        "secret": "'${KEYCLOAK_CLIENT_SECRET:-ragchat-secret}'"
    }' \
    http://localhost:8080/admin/realms/ragchat/clients

echo "Client created. Creating user..."

# Create a test user
curl -s -X POST \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "testuser",
        "enabled": true,
        "emailVerified": true,
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User",
        "credentials": [{
            "type": "password",
            "value": "password",
            "temporary": false
        }]
    }' \
    http://localhost:8080/admin/realms/ragchat/users

echo "User created. Setup complete!" 
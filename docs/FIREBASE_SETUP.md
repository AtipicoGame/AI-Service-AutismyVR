# Firebase Authentication Setup

Este documento explica como configurar a autenticação Firebase na API para integrar com o Unity.

## Pré-requisitos

1. Projeto Firebase criado no [Firebase Console](https://console.firebase.google.com/)
2. Firebase Authentication habilitado no projeto
3. Service Account Key do Firebase (para validação server-side)

## Configuração

### 1. Obter Service Account Key

1. Acesse o [Firebase Console](https://console.firebase.google.com/)
2. Selecione seu projeto
3. Vá em **Project Settings** (ícone de engrenagem)
4. Aba **Service Accounts**
5. Clique em **Generate New Private Key**
6. Salve o arquivo JSON (ex: `firebase-service-account.json`)

### 2. Configurar Variáveis de Ambiente

Você pode configurar o Firebase de três formas:

#### Opção 1: Arquivo de Credenciais (Recomendado para desenvolvimento)

```bash
export FIREBASE_CREDENTIALS_PATH=/caminho/para/firebase-service-account.json
```

#### Opção 2: JSON como String (Recomendado para Docker/Produção)

```bash
export FIREBASE_CREDENTIALS_JSON='{"type":"service_account","project_id":"..."}'
```

#### Opção 3: Default Credentials (GCP/Cloud Run)

Se estiver rodando no Google Cloud, o Firebase usará as credenciais padrão automaticamente.

### 3. Atualizar Docker Compose (Opcional)

Se usar Docker, adicione ao `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      - FIREBASE_CREDENTIALS_PATH=/app/firebase-service-account.json
    volumes:
      - ./firebase-service-account.json:/app/firebase-service-account.json:ro
```

## Como Funciona

### No Unity (Cliente)

O Unity já deve estar configurado para autenticar com Firebase. Após o login, você obtém um **Firebase ID Token**:

```csharp
// Exemplo Unity/C#
FirebaseAuth.DefaultInstance.CurrentUser.TokenAsync(true).ContinueWith(task => {
    if (task.IsCompleted) {
        string idToken = task.Result;
        // Enviar este token no header Authorization
    }
});
```

### Na API (Servidor)

1. Cliente envia requisição com header: `Authorization: Bearer <firebase_id_token>`
2. API valida o token usando Firebase Admin SDK
3. Se válido, extrai `uid` do usuário
4. Endpoints acessam `g.firebase_uid` para identificar o usuário

## Endpoints Protegidos

Todos os endpoints agora requerem autenticação:

- `POST /chat` - Enviar mensagem ao AI
- `GET /history/<session_id>` - Obter histórico de uma sessão
- `GET /sessions` - Listar todas as sessões do usuário

## Exemplo de Requisição

```bash
curl -X POST http://localhost:5001/chat \
  -H "Authorization: Bearer <firebase_id_token>" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!", "session_id": null}'
```

## Migração do Banco de Dados

⚠️ **IMPORTANTE**: O modelo `ChatSession` agora inclui `firebase_uid`. Você precisará:

1. **Desenvolvimento**: Recriar o banco (dados serão perdidos)
   ```bash
   # O init_db() já cria as novas colunas
   ```

2. **Produção**: Criar migration para adicionar a coluna:
   ```sql
   ALTER TABLE chat_sessions ADD COLUMN firebase_uid VARCHAR(128) NOT NULL DEFAULT '';
   CREATE INDEX idx_firebase_uid ON chat_sessions(firebase_uid);
   ```

## Testando

### 1. Teste Manual

1. Obtenha um token do Firebase (via Unity ou Firebase Console)
2. Use o Swagger em `http://localhost:5001/apidocs`
3. Clique em "Authorize" e cole o token
4. Teste os endpoints

### 2. Teste com Postman/Insomnia

1. Configure header: `Authorization: Bearer <token>`
2. Faça requisições aos endpoints

## Troubleshooting

### Erro: "Failed to initialize Firebase"
- Verifique se `FIREBASE_CREDENTIALS_PATH` ou `FIREBASE_CREDENTIALS_JSON` está configurado
- Verifique se o arquivo JSON existe e é válido

### Erro: "Invalid ID token"
- Token pode estar expirado (tokens Firebase expiram após 1 hora)
- Token pode ser inválido
- Verifique se o projeto Firebase está correto

### Erro: "Missing Authorization header"
- Certifique-se de enviar o header: `Authorization: Bearer <token>`
- O formato deve ser exatamente: `Bearer <espaço><token>`


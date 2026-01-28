### 🎤 [00:30:47 – 00:33:32] Endpoints and keys  
**Timestamp**: 00:30:47 – 00:33:32

**Key Concepts**  
- AI services expose endpoints (URLs) that applications communicate with.  
- Communication with endpoints is typically via REST (HTTP-based) and returns JSON responses.  
- SDKs often provide language-friendly libraries that handle REST calls internally.  
- Authentication to endpoints requires keys or integrated identity solutions.  
- Secure storage of keys is critical (e.g., Azure Key Vault).  
- Role-based access control (RBAC) and Azure Entra ID integrated authentication can eliminate the need to store keys.  
- Managed identities in Azure provide automatic identities for resources to access services securely without keys.  

**Definitions**  
- **Endpoint**: A URL address exposed by an AI service that an application connects to for interaction.  
- **REST Endpoint**: An HTTP-based interface that accepts requests and returns JSON responses.  
- **SDK (Software Development Kit)**: A set of libraries that simplify interacting with REST endpoints in a programming language.  
- **Key**: A secret token used to authenticate and authorize access to an AI service endpoint.  
- **Azure Key Vault**: A secure service to store keys and secrets, preventing them from being exposed in code or repositories.  
- **Entra ID Integrated Authentication**: An authentication method using Azure Active Directory identities and RBAC instead of keys.  
- **Managed Identity**: An automatically managed identity assigned to Azure resources to authenticate to services without storing credentials.  

**Key Facts**  
- Endpoints are REST-based and return JSON responses.  
- Each endpoint has associated keys (usually two) for authentication.  
- Keys should not be stored in config files or Git repositories.  
- Azure services support RBAC with Entra ID to avoid key management.  
- Managed identities simplify permission management and key rotation concerns.  

**Examples**  
- Viewing a vision AI resource in Azure shows the endpoint URL and two keys.  
- An application can fetch keys securely from Azure Key Vault or use Entra ID integrated auth with assigned roles.  

**Key Takeaways 🎯**  
- Always secure your keys; do not hardcode or expose them publicly.  
- Prefer using Azure Entra ID integrated authentication and managed identities for better security and easier management.  
- Use SDKs to simplify interaction with REST endpoints.  
- Understand that endpoints are the main access points for AI services and require proper authentication.  
- Role-based access control helps assign precise permissions without sharing keys.
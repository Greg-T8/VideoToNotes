### 🎤 [02:56:41 – 03:00:30] Access  
**Timestamp**: 02:56:41 – 03:00:30

**Key Concepts**  
- Storage account access keys and their management  
- Role-Based Access Control (RBAC) on the data plane for granular permissions  
- Shared Access Signatures (SAS) for scoped, time-limited access  
- Encryption options for storage data  

**Definitions**  
- **Access Keys**: Two keys provided per storage account to authenticate and authorize access; having two allows key rotation without service interruption.  
- **Data Plane Role-Based Access Control (RBAC)**: Permissions assigned to users or service principals specifically for data operations (e.g., Blob Data Reader, Blob Data Contributor).  
- **Shared Access Signature (SAS)**: A token signed by an access key that grants limited and time-bound access to storage resources at either the account or service level.  
- **Customer Managed Key (CMK)**: Encryption key stored and managed in Azure Key Vault, used instead of platform-managed keys for encrypting storage data.  

**Key Facts**  
- Storage accounts have two access keys to enable seamless key regeneration and rotation.  
- RBAC roles include Blob Data Reader, Blob Data Contributor, Blob Data Owner, File Data, Queue Data, and Table Data roles.  
- Access keys can be disabled to block their use entirely; however, disabling access keys also disables SAS tokens since SAS tokens are signed by access keys.  
- SAS tokens allow granular control over permissions, services, time validity, and IP ranges.  
- Encryption by default uses Microsoft-managed platform keys; customers can opt for customer-managed keys via Azure Key Vault.  

**Examples**  
- Regenerating one access key while using the other to avoid service interruption.  
- Creating a shared access signature at the storage account level with specific permissions, time frames, and IP restrictions.  
- Creating a service-level SAS token with defined properties and duration.  

**Key Takeaways 🎯**  
- Use two access keys to enable seamless key rotation without downtime.  
- Prefer RBAC on the data plane over using access keys for better security and granular permissions.  
- Understand that disabling access keys disables SAS tokens, so plan accordingly.  
- Leverage SAS tokens for fine-grained, temporary access control to storage resources.  
- Consider customer-managed keys for encryption if you require control over key management beyond the default platform-managed keys.
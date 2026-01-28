### 🎤 [00:03:06 – 00:04:01] User delegated SAS for more services  
**Timestamp**: 00:03:06 – 00:04:01

**Key Concepts**  
- User-delegated Shared Access Signatures (SAS) are now extended to Azure Tables, Files, and Queues (previously available for Blobs).  
- User delegation SAS provides a more secure way to grant limited access to storage resources.  
- Unlike account or service SAS, user delegation SAS is signed by an Azure AD (Entra ID) identity rather than storage account keys.  
- Permissions granted by user delegation SAS cannot exceed those of the delegating identity.  
- User delegation SAS tokens have a maximum validity period of seven days.

**Definitions**  
- **User Delegation SAS**: A type of Shared Access Signature signed by an Azure AD identity, providing delegated and more secure access to storage services.  
- **Account/Service SAS**: SAS tokens signed by storage account keys, which have broad and powerful permissions.

**Key Facts**  
- User delegation SAS is now available for Tables, Files, and Queues in addition to Blobs.  
- User delegation SAS tokens can only be valid for up to seven days.  
- The SAS token’s permissions are limited by the permissions of the Azure AD identity that creates it.

**Examples**  
- None mentioned explicitly.

**Key Takeaways 🎯**  
- User delegation SAS enhances security by leveraging Azure AD identities instead of storage account keys.  
- It limits the scope and lifetime of access tokens, reducing risk.  
- Extending user delegation SAS to more storage services broadens secure access options across Azure Storage.
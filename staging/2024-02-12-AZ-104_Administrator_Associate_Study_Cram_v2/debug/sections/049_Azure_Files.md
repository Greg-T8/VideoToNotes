### 🎤 [02:52:45 – 02:56:41] Azure Files  
**Timestamp**: 02:52:45 – 02:56:41

**Key Concepts**  
- Azure Files provides fully managed file shares in the cloud, accessible via SMB protocol.  
- Supports multiple performance tiers: transaction optimized, hot, cool, and premium storage accounts.  
- Features include soft delete, backup snapshots, and integration with Azure AD (Entra ID) for data plane access control.  
- Azure File Sync enables synchronization between on-premises Windows file shares and Azure Files.  
- Tiering capability in Azure File Sync allows offloading less-used files to the cloud to save local storage space.  

**Definitions**  
- **Azure Files**: A cloud service that offers fully managed file shares accessible via SMB protocol, supporting various performance tiers and data protection features.  
- **Soft Delete**: A feature that allows recovery of deleted files for a configurable retention period (between 1 and 365 days).  
- **Azure File Sync**: A service that synchronizes file shares between on-premises Windows servers and Azure Files, enabling hybrid file storage solutions.  
- **Sync Group**: A logical grouping in Azure File Sync that contains one cloud endpoint and up to 100 server endpoints to synchronize data.  
- **Tiering**: A feature in Azure File Sync that moves infrequently accessed files to the cloud while keeping placeholders locally, freeing up on-premises storage.  

**Key Facts**  
- Soft delete retention can be set from 1 up to 365 days; default example given is 14 days.  
- Backup snapshots can be configured to capture point-in-time states of file shares.  
- Azure File Sync supports up to 100 server endpoints per sync group, with exactly one cloud endpoint.  
- Tiering triggers when local free space drops below a configured threshold, offloading least used files to Azure Files.  
- Azure Files integrates with Entra ID (Azure AD) for data plane permissioning, similar to Azure Blob storage.  

**Examples**  
- A user has multiple Windows file shares on-premises and creates an Azure Files SMB share in the cloud. Using Azure File Sync, these shares can be synchronized to the cloud endpoint.  
- Tiering example: When local file server space is low, least used files are tiered to Azure Files, leaving a thumbnail/link locally that fetches the file on demand.  

**Key Takeaways 🎯**  
- Azure Files offers flexible, tiered cloud file storage with strong data protection features like soft delete and snapshots.  
- Azure File Sync bridges on-premises and cloud file shares, enabling hybrid scenarios and seamless data access.  
- Tiering helps manage limited on-premises storage by offloading cold data to the cloud without disrupting user access.  
- Integration with Azure AD enhances security by enabling granular access control at the data plane level.  
- Having two storage account access keys allows seamless key regeneration without service interruption.  

---
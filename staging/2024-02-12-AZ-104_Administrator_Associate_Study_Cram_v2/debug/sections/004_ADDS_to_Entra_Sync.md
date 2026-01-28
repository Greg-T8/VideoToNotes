### 🎤 [00:05:01 – 00:07:59] ADDS to Entra Sync  
**Timestamp**: 00:05:01 – 00:07:59

**Key Concepts**  
- Replication flow is one-way: from Active Directory Domain Services (AD DS) to Entra ID (Azure AD).  
- Two main technologies for syncing AD DS to Entra ID: Entra Connect Sync and Entra Connect Cloud Sync.  
- Entra Connect Sync runs on-premises on a Windows Server instance.  
- Entra Connect Cloud Sync runs in the cloud with lightweight agents on domain controllers.  
- Once identities are synced to Entra ID, applications trust Entra ID for authentication and authorization.  
- Entra ID tenant acts as the organizational instance containing users, groups, devices, applications, and policies.  
- Entra ID supports authentication for Microsoft services (Azure, Microsoft 365) and third-party SaaS applications.  
- Entra ID can integrate with secure service edge solutions, enabling control over internet access and on-premises TCP/UDP applications via Entra Private Access.

**Definitions**  
- **Entra Connect Sync**: An on-premises synchronization engine running on Windows Server that syncs identities from AD DS to Entra ID.  
- **Entra Connect Cloud Sync**: A cloud-based synchronization service where the engine runs in the cloud, using lightweight agents installed on domain controllers to communicate.  
- **Source of Truth**: AD DS is considered the authoritative source for identity information, which is then replicated to Entra ID.  
- **Tenant**: A dedicated instance of Entra ID for an organization, containing its users, groups, devices, applications, and policies.

**Key Facts**  
- Sync direction is always from AD DS to Entra ID, never the reverse.  
- Entra Connect Cloud Sync uses lightweight agents on domain controllers but the main engine runs in the cloud.  
- Entra Connect Sync engine runs as an application on a Windows Server instance on-premises.  
- Entra ID tenants can be named, e.g., "SavileTech.net" as an example tenant name.

**Examples**  
- Example tenant name: SavileTech.net  
- Applications trusting Entra ID for authentication include Azure, Microsoft 365, and numerous third-party SaaS apps.  
- Entra Private Access can control access to any TCP or UDP on-premises application and internet sites through secure service edge integration.

**Key Takeaways 🎯**  
- Always remember the sync flow direction: AD DS → Entra ID.  
- Choose between Entra Connect Sync (on-premises) and Entra Connect Cloud Sync (cloud-based) depending on infrastructure needs.  
- Entra ID acts as a central identity provider trusted by Microsoft and third-party applications.  
- Integration with secure service edge solutions extends identity-based access control beyond cloud apps to internet and on-premises resources.  
- Your organization’s Entra ID tenant is the core container for identity and access management policies.
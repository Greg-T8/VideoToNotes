### 🎤 [00:11:08 – 00:15:51] Users  
**Timestamp**: 00:11:08 – 00:15:51

**Key Concepts**  
- User accounts within a tenant can be cloud-native or synchronized from on-premises Active Directory (hybrid).  
- External users (guests) can come from other identity providers or tenants, enabling collaboration without creating separate accounts.  
- Different user types: native cloud accounts, synchronized hybrid accounts, and guest/external accounts.  
- External users can be assigned as guests or members, affecting policy application.  
- Primary identity of external users remains with their original identity provider (e.g., other Entra tenants, Microsoft accounts, Google, Facebook, SAML).  
- Account provisioning can be done manually, via synchronization, or through automated provisioning endpoints (e.g., HR systems, APIs).  
- Bulk user operations are supported for creation and invitation, using CSV templates or scripts.  
- Groups are used to manage permissions and licenses more efficiently than assigning them individually to users.

**Definitions**  
- **Cloud Account**: A user account created directly in the cloud tenant.  
- **Hybrid Account**: A user account created in on-premises Active Directory and synchronized to the cloud tenant.  
- **Guest User**: An external user invited from another identity provider or tenant, who accesses resources without having a native account in the tenant.  
- **Member User**: An external user who is assigned as a member in the tenant, which can affect policy application.  
- **Provisioning Endpoint**: A system or API that automates the creation and management of user accounts, potentially integrating with HR systems or Active Directory.

**Key Facts**  
- External users can authenticate via various identity providers including other Entra tenants, Microsoft accounts, Google, Facebook, SAML, or via one-time email codes.  
- Provisioning can be integrated with HR systems or other external sources, which may create accounts in Active Directory first and then replicate to Entra.  
- Bulk user creation and invitation are supported through CSV templates and scripting.  
- Managing permissions via groups is more scalable than assigning roles or licenses to individual users.

**Examples**  
- A guest user invited from a different Entra tenant.  
- Guest users authenticated via Google, Facebook, Microsoft accounts, or SAML providers.  
- Provisioning accounts from an HR system through Entra provisioning endpoints.  
- Bulk creating users by uploading a CSV template in the portal.

**Key Takeaways 🎯**  
- Understand the distinction between cloud-native, hybrid, and guest user accounts.  
- External users improve collaboration without requiring separate credentials or accounts in your tenant.  
- Provisioning can be automated and integrated with existing systems like HR or Active Directory.  
- Bulk operations simplify large-scale user management tasks.  
- Use groups to efficiently manage permissions and licenses instead of assigning them individually.
### 🎤 [00:02:20 – 00:05:01] Entra ID  
**Timestamp**: 00:02:20 – 00:05:01

**Key Concepts**  
- Entra ID is the new name for what was formerly known as Azure AD.  
- Entra ID is Microsoft’s cloud-based identity provider.  
- It uses modern internet protocols for authentication and authorization, such as OAuth 2, OpenID Connect, SAML, and WS-Fed.  
- Communication with Entra ID happens over HTTPS (port 443) using TLS encryption, making it internet-friendly without requiring multiple network ports.  
- Entra ID contrasts with traditional on-premises Active Directory Domain Services (AD DS), which uses protocols like Kerberos, NTLM, and LDAP and requires multiple ports on private networks.  
- Interaction with Entra ID is primarily done through Microsoft Graph API, which uses REST-based calls over HTTPS.  
- Entra ID has a flat structure, unlike AD DS which has organizational units; however, Entra ID supports administrative units for granular permission delegation.  
- Common practice involves syncing on-premises AD DS to Entra ID, with AD DS as the source of truth.  

**Definitions**  
- **Entra ID**: Microsoft’s cloud-based identity provider, formerly known as Azure AD, designed for internet-based authentication and authorization.  
- **Microsoft Graph**: The standard REST API used to interact with Entra ID and other Microsoft 365 services.  
- **Administrative Units**: A feature in Entra ID that allows delegation of permissions at a more granular level, compensating for the lack of organizational units.  

**Key Facts**  
- Entra ID communicates using internet protocols: OAuth 2, OpenID Connect, SAML, WS-Fed.  
- All communication is secured via HTTPS (port 443) and TLS encryption.  
- On-premises AD DS uses Kerberos, NTLM, LDAP, and requires multiple network ports.  
- Entra ID is primarily flat in structure, unlike the hierarchical structure of AD DS.  
- Sync from AD DS to Entra ID is one-way: AD DS is the source of truth.  

**Examples**  
- None specifically mentioned beyond protocol and API usage examples.  

**Key Takeaways 🎯**  
- Understand that Entra ID is the cloud evolution of Azure AD and serves as a modern identity provider optimized for internet protocols.  
- Remember the key protocols used for authentication and authorization in Entra ID (OAuth 2, OpenID Connect, SAML).  
- Know that Entra ID uses Microsoft Graph API for management and interaction, which is REST-based over HTTPS.  
- Recognize the structural difference: Entra ID is flat but supports administrative units for permission delegation.  
- Be aware that syncing from on-premises AD DS to Entra ID is common, with AD DS remaining the authoritative source.
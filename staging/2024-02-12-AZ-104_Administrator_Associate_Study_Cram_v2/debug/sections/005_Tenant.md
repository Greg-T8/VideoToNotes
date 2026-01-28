### 🎤 [00:07:59 – 00:10:21] Tenant  
**Timestamp**: 00:07:59 – 00:10:21

**Key Concepts**  
- An Entra tenant represents an organization’s dedicated instance containing users, groups, devices, applications, and policies.  
- Tenants are global instances, independent of Azure subscriptions.  
- Custom domains can be added and verified to a tenant, replacing the default onmicrosoft.com domain.  
- Tenants support company branding to customize user experience during sign-in and access.

**Definitions**  
- **Tenant**: A specific organizational instance in Entra ID that holds users, groups, devices, applications, and conditional access policies.  
- **Custom Domain**: A verified domain name added to a tenant to replace the default onmicrosoft.com domain for user identities and branding.

**Key Facts**  
- Default tenant domain format is `something.onmicrosoft.com`.  
- Custom domains require DNS verification by adding a record in the domain’s zone to prove ownership.  
- After verification, the custom domain can be set as the primary domain for the tenant.  
- Tenants do not reside within Azure subscriptions; subscriptions trust tenants but tenants are global and independent.  
- Company branding options include configuring backgrounds, images, and sign-in messages with formatting (bold, underline).

**Examples**  
- The speaker’s tenant example: `savilltech.net` as a custom domain added and set as the primary domain.  
- The default domain before adding custom domain is something like `something.onmicrosoft.com`.

**Key Takeaways 🎯**  
- Understand that a tenant is a global, organizational instance separate from Azure subscriptions.  
- Always verify custom domains via DNS to use them within a tenant.  
- Custom domains improve identity management and branding within Entra ID.  
- Company branding allows tailoring the user sign-in experience for better organizational identity.
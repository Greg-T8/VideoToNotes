### 🎤 [00:59:09 – 01:06:56] RBAC  
**Timestamp**: 00:59:09 – 01:06:56

**Key Concepts**  
- Role-Based Access Control (RBAC) assigns permissions to identities (users, groups, service principals) at specific scopes within Azure.  
- Azure resources are organized hierarchically: management groups > subscriptions > resource groups > individual resources. RBAC roles can be assigned at any of these scopes.  
- Least privilege principle: assign the minimum permissions needed at the smallest possible scope to reduce risk.  
- Roles are collections of actions that apply to resource providers and their resources.  
- Role assignments link an identity, a role, and a scope.  
- Built-in roles include Owner, Contributor, Reader, each with different permission levels.  
- Custom roles can be created by cloning existing roles and adding/removing specific permissions to tailor access precisely.  
- Role assignments are inherited down the resource hierarchy (e.g., a role assigned at a management group applies to all underlying subscriptions and resources).  
- RBAC roles differ from Entra roles, which apply to tenant-level permissions.  
- User Access Administrator role allows elevating permissions across subscriptions that trust the tenant.  
- Resource locks can be applied at subscription, resource group, or resource level to prevent deletion or make resources read-only.

**Definitions**  
- **Role**: A set of permissions (actions) that can be assigned to an identity for managing Azure resources.  
- **Scope**: The level at which a role assignment applies (management group, subscription, resource group, or resource).  
- **Role Assignment**: The binding of an identity to a role at a specific scope.  
- **Owner**: Built-in role with full permissions including managing access.  
- **Contributor**: Built-in role with permissions to manage resources but cannot manage access.  
- **Reader**: Built-in role with read-only access to resources.  
- **Custom Role**: A user-defined role created by modifying existing roles to fit specific permission needs.  
- **User Access Administrator**: A role that allows a user to grant access to Azure resources, often used by global admins to elevate permissions.  
- **Resource Lock**: A mechanism to prevent accidental deletion or modification of resources, with two types: Delete lock and Read-only lock.

**Key Facts**  
- Owner role can have up to 16,000 permissions because it can perform any action on any resource.  
- Role assignments can be inherited from higher scopes down to individual resources.  
- Custom roles allow adding or excluding specific permissions, including wildcard permissions with exceptions.  
- RBAC roles apply to Azure resources, while Entra roles apply to tenant-level permissions.  
- User Access Administrator permission can be granted at the root scope to enable permission elevation across subscriptions.  
- Locks can be applied at multiple levels and are either "cannot delete" or "read-only."

**Examples**  
- Network team given a role at a high management group level to manage virtual networks across the entire structure.  
- A subscription user might have a role only at the subscription or resource group level for limited access.  
- Viewing access control on a resource group shows many possible roles because it contains many resource types.  
- Viewing access control on a container registry or storage account shows fewer roles relevant to that resource type.  
- A BLOB data owner role assigned directly on a storage resource.  
- A managed identity assigned a role on a specific virtual machine resource.  
- Creating a custom role by cloning an existing role and removing write or delete permissions to enforce least privilege.

**Key Takeaways 🎯**  
- Always apply the principle of least privilege: assign only the permissions necessary at the smallest scope possible.  
- Use groups for role assignments rather than individual users to simplify management and avoid orphaned permissions.  
- Understand role inheritance and how assignments at higher scopes affect all underlying resources.  
- Be cautious with powerful built-in roles like Owner; avoid over-assigning these roles.  
- Custom roles are valuable for tailoring permissions when built-in roles are too broad.  
- RBAC roles are distinct from Entra roles; know which applies to your scenario.  
- Use User Access Administrator role carefully to enable permission elevation when needed.  
- Implement resource locks to protect critical resources from accidental deletion or modification.
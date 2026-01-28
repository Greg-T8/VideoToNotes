### 🎤 [00:25:00 – 00:27:23] Roles  
**Timestamp**: 00:25:00 – 00:27:23

**Key Concepts**  
- Roles define sets of permissions assigned to users or groups within an organization.  
- The **Global Administrator** role is the most privileged and should be tightly controlled.  
- Delegated roles allow assigning specific permissions without granting full admin rights.  
- Administrative Units enable granular role assignment scoped to specific users, groups, or devices.  
- Permissions granted via roles in an administrative unit apply only to objects within that unit.  
- Adding a group to an administrative unit does not automatically grant role permissions over the users in that group; users must be explicitly added to the administrative unit for role permissions to apply.  

**Definitions**  
- **Global Administrator**: The highest privilege role with broad access across the organization; should be restricted to trusted individuals.  
- **Administrative Units**: Containers that group users, groups, and devices to allow scoped role assignments limited to those objects.  

**Key Facts**  
- Role assignments can be scoped to administrative units for more granular control.  
- Role permissions do not cascade from groups to their members within administrative units unless users are explicitly added.  
- This explicit user addition is a safety feature to prevent unintended permission escalation.  

**Examples**  
- Assigning a role to manage a specific group within an administrative unit without granting permissions over the users in that group unless those users are also added to the unit.  

**Key Takeaways 🎯**  
- Restrict the Global Administrator role due to its high level of privilege.  
- Use delegated roles to provide only necessary permissions.  
- Leverage administrative units to limit role scope and improve security management.  
- Always explicitly add users to administrative units if role permissions over those users are required, even if their group is already in the unit.  
- This approach prevents accidental over-permissioning and maintains clear boundaries of administrative control.
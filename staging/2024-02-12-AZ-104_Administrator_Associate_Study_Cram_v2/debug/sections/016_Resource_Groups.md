### 🎤 [00:43:31 – 00:45:39] Resource Groups  
**Timestamp**: 00:43:31 – 00:45:39

**Key Concepts**  
- Resource groups are a deployment and management container within an Azure subscription.  
- Multiple resource groups can exist within a single subscription, but resource groups cannot be nested inside one another.  
- Role-Based Access Control (RBAC), policies, and budgets can be applied at the resource group level for granular management.  
- Resources such as virtual machines, storage accounts, load balancers, etc., are created inside resource groups.  
- Resource groups are used to logically group resources that are provisioned, run, and decommissioned together.  
- Grouping resources by application or functionality helps with access control, policy application, and cost tracking.

**Definitions**  
- **Resource Group**: A container within an Azure subscription that holds related resources which share lifecycle, access control, policies, and budgeting.

**Key Facts**  
- Resource groups cannot be nested; each resource group exists independently within a subscription.  
- RBAC, policies, and budgets can be applied specifically to resource groups to manage subsets of resources more granularly.  
- Grouping resources in a resource group facilitates tracking spend and applying common controls.

**Examples**  
- A resource group might contain a set of virtual machines, a Kubernetes environment, a load balancer, and a database that together form a business application.  
- Resources that are provisioned, run, and deleted together (e.g., all components of a specific application) are placed in the same resource group.

**Key Takeaways 🎯**  
- Use resource groups to organize resources that share a common lifecycle and purpose.  
- Apply RBAC, policies, and budgets at the resource group level for more precise governance and cost control.  
- Resource groups help in tracking costs and managing access for specific applications or workloads within a subscription.  
- Logical grouping of resources simplifies management and aligns with business or operational units.
### 🎤 [00:34:48 – 00:39:14] Subscriptions and Management Groups  
**Timestamp**: 00:34:48 – 00:39:14

**Key Concepts**  
- Azure resources are deployed within **subscriptions**, which serve as organizational and billing boundaries.  
- Subscriptions are tied to a specific **tenant** and trust that tenant.  
- **Management groups** provide a hierarchy above subscriptions to organize and govern multiple subscriptions.  
- Management groups enable centralized governance, role assignment, policy enforcement, and budget tracking across multiple subscriptions.  
- Policies, roles, and budgets set at management group levels are **inherited** by all child management groups and subscriptions.  
- Governance includes role-based access control (RBAC), Azure Policy for enforcing rules, and budget management for financial control.  
- The hierarchy can be structured based on geography, business units, environment (prod/non-prod), or other organizational needs.  
- Cost management and billing tools are available at subscription and management group levels to monitor and forecast spending.

**Definitions**  
- **Tenant**: The overarching Azure Active Directory instance that owns and manages subscriptions.  
- **Subscription**: A container for Azure resources that provides a billing and organizational boundary, tied to a specific tenant.  
- **Management Group**: A container that holds subscriptions and other management groups, allowing for hierarchical organization and centralized governance.  
- **Role-Based Access Control (RBAC)**: A system to assign permissions to users or groups at different scopes (management group, subscription, resource).  
- **Azure Policy**: A governance tool to enforce rules and guardrails on resources, such as restricting resource types or regions.  
- **Budget**: A financial control mechanism to track and limit spending within subscriptions or management groups.

**Key Facts**  
- The **root management group** exists at the tenant level and is the top of the hierarchy.  
- Subscriptions can be directly under the root management group or nested inside child management groups.  
- Management groups support three core governance features: **Access Control (RBAC), Policy, and Budgets**.  
- Policies, roles, and budgets set at higher levels cascade down to all child entities.  
- Azure offers **free trial accounts** and some always-free services to start experimenting without cost.  
- Azure is **consumption-based billing**: you pay only for what you use, so managing resources and costs is critical.  
- Cost analysis and cost management tools are accessible via the Azure portal to monitor spending and forecast costs.

**Examples**  
- Example hierarchy:  
  - Tenant root management group  
    - One subscription tied directly to root  
    - Child management group "All Savile Tech Subscriptions"  
      - Two subscriptions under this child group  
      - Two further child management groups under it  
- Governance scenarios:  
  - Assigning roles at management group level to control access across multiple subscriptions.  
  - Applying policies to restrict resource types or enforce agent installation.  
  - Setting budgets to monitor and control financial spend across environments.

**Key Takeaways 🎯**  
- Use **subscriptions** to organize resources and manage billing boundaries.  
- Build a **management group hierarchy** to simplify governance across multiple subscriptions.  
- Apply **RBAC, policies, and budgets** at management group levels for consistent, inherited governance.  
- Structure management groups based on organizational needs like geography, business units, or environment types.  
- Always monitor costs using Azure’s cost management tools to avoid unexpected charges.  
- Take advantage of free trials and always-free services to experiment and learn without financial risk.  
- Remember that governance settings applied higher in the hierarchy cascade down, enabling centralized control.
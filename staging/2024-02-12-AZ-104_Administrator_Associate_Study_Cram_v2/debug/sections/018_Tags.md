### 🎤 [00:51:20 – 00:54:35] Tags  
**Timestamp**: 00:51:20 – 00:54:35

**Key Concepts**  
- Tags are key-value pairs applied to Azure resources, resource groups, or subscriptions to add metadata.  
- Tags help organize, filter, and manage resources beyond the default hierarchy of subscriptions and resource groups.  
- Tags are not inherited automatically from parent scopes (subscription → resource group → resource).  
- Azure Policy can be used to enforce or copy tags from parent scopes to child resources.  
- Tags can be used for billing, filtering views, and tracking ownership or environment details.

**Definitions**  
- **Tag**: A key-value pair assigned to Azure resources, resource groups, or subscriptions to store metadata for organizational or billing purposes.  
- **Inheritance (in context of tags)**: The automatic application of tags from a parent resource (subscription or resource group) to child resources, which does not happen by default in Azure.

**Key Facts**  
- Typically, up to 50 tags can be applied per resource or resource group.  
- Tags set at the subscription level do NOT propagate to resource groups or resources.  
- Tags set at the resource group level do NOT propagate to individual resources.  
- Azure Policy can be configured to copy or enforce tags from parent to child resources, enabling inheritance-like behavior.  

**Examples**  
- Applying a tag at the subscription level: e.g., `environment=dev` on a dev subscription.  
- Applying tags to resource groups or individual resources such as:  
  - `owner` to track who is responsible for a resource  
  - `OS version` to track the operating system version  
  - `cost center` or `business unit` for billing and organizational tracking  
- Filtering resources by tag values, e.g., showing only resources where `cost center=demo group one`.

**Key Takeaways 🎯**  
- Tags are a flexible way to add metadata to Azure resources for management, billing, and filtering.  
- Tags do not inherit automatically; each level (subscription, resource group, resource) must have tags set explicitly unless Azure Policy is used.  
- Using Azure Policy to enforce or copy tags can help maintain consistent tagging standards across resources.  
- Tags improve visibility and control in large environments by enabling filtering and reporting based on metadata.
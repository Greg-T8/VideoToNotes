### 🎤 [00:45:39 – 00:51:20] Cost saving mechanisms  
**Timestamp**: 00:45:39 – 00:51:20

**Key Concepts**  
- Cost optimization involves both operational actions (like sizing and stopping resources) and financial mechanisms to reduce Azure bills.  
- Azure Hybrid Benefit allows use of existing on-premises licenses in the cloud to reduce licensing costs.  
- Azure Reservations provide discounts by committing to specific services in specific regions for 1 or 3 years.  
- Azure Savings Plan offers flexible discounts on included compute services with a commitment of 1 or 3 years.  
- Savings Plan discounts vary by SKU and service type and apply hourly to running resources.  
- Only one financial discount mechanism (Savings Plan or Reserved Instance) can apply to a resource at a time.  
- Tags can be applied to subscriptions, resource groups, or resources to add metadata useful for filtering and billing.

**Definitions**  
- **Azure Hybrid Benefit**: A licensing benefit that lets you use existing Windows Server, SQL Server, or Red Hat Enterprise Linux licenses with software assurance in Azure, reducing consumption costs.  
- **Azure Reservations**: A pricing option where you pre-pay or commit to use a specific Azure service in a specific region for 1 or 3 years to receive a discount.  
- **Azure Savings Plan**: A flexible pricing commitment for included compute services that provides discounts based on hourly spend over 1 or 3 years, applicable across multiple SKUs and services.  
- **Tags**: Key-value pairs applied to Azure resources, resource groups, or subscriptions to add metadata for organization, filtering, and billing purposes.

**Key Facts**  
- Azure Hybrid Benefit applies to Windows Server (Standard or Datacenter), SQL Server, and Red Hat Enterprise Linux licenses.  
- Standard Windows Server licenses must be moved to the cloud to use Hybrid Benefit; Datacenter licenses can be used both on-premises and in the cloud simultaneously.  
- Azure Reservations require specificity in service and region to qualify for discounts.  
- Savings Plans apply only to included compute services such as many VM types, Azure Dedicated Hosts, and certain App Service plans.  
- Commitment terms for Reservations and Savings Plans are typically 1 or 3 years.  
- Savings Plan discounts vary by SKU; newer SKUs may have better discounts.  
- Billing applies discounts hourly, prioritizing the best discount for running resources.  
- Storage accounts can have Reserved Instances but do not support Savings Plans.  
- Financial cost-saving options do not involve resizing or stopping VMs but focus on licensing and commitment discounts.

**Examples**  
- Using Azure Hybrid Benefit to remove Windows Server or SQL Server license costs from the VM pricing.  
- Comparing discounts on different VM SKUs (e.g., V5 SKU has better Savings Plan discount than older SKUs).  
- Applying a 3-year Reserved Instance or Savings Plan commitment to reduce compute costs.  

**Key Takeaways 🎯**  
- Leverage Azure Hybrid Benefit to reduce licensing costs by using existing licenses in the cloud.  
- Use Azure Reservations for predictable workloads where you can commit to specific services and regions to save money.  
- Consider Azure Savings Plans for more flexible compute usage with discounts applied hourly across eligible services.  
- Only one discount mechanism (Savings Plan or Reserved Instance) can be applied to a resource at a time—choose based on workload predictability and flexibility needs.  
- Tags are important for organizing resources and can support cost tracking and billing analysis.  
- Financial cost-saving mechanisms complement operational optimizations like right-sizing and stopping unused resources.
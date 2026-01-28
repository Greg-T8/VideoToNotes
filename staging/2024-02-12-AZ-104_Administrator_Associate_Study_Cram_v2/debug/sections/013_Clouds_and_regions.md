### 🎤 [00:27:23 – 00:34:48] Clouds and regions  
**Timestamp**: 00:27:23 – 00:34:48

**Key Concepts**  
- Multiple Azure clouds/environments exist beyond the well-known Azure Commercial Cloud.  
- Each cloud/environment has its own control plane URLs and separate Azure AD (Entra) tenants.  
- Resources are deployed into regions, which are geographic locations containing multiple data centers.  
- Regions are subdivided into availability zones (AZs), typically three per region, representing separate data centers for resiliency.  
- Deployment options include zonal (within a single AZ) or zone-redundant (spanning multiple AZs) for higher availability.  
- Azure has many global regions, each with different availability zone support and sustainability info.  
- Regions are paired for safe deployment rollouts and disaster recovery, usually within the same geopolitical boundary.  
- Pairings are used by Microsoft for staged rollouts but customers are not required to use paired regions exclusively.  
- Selecting regions depends on latency, data sovereignty, and resiliency needs.  
- Subscriptions are the deployment boundary and trust a specific tenant.

**Definitions**  
- **Cloud/Environment**: A distinct Azure instance such as Azure Commercial, Azure US Gov, or Azure China, each with separate control planes and tenants.  
- **Region**: A geographic area containing multiple data centers where Azure resources are deployed.  
- **Availability Zone (AZ)**: Physically separate data centers within a region designed to provide redundancy and high availability.  
- **Zonal Deployment**: Deploying a resource within a single availability zone.  
- **Zone-Redundant Deployment**: Deploying a resource across multiple availability zones for resiliency.  
- **Paired Regions**: Two Azure regions geographically paired to enable safe deployment rollouts and disaster recovery.

**Key Facts**  
- Azure exposes 3 availability zones per region to subscriptions, even if more physically exist.  
- Regions should be chosen with large physical distance (hundreds of miles) between them to mitigate natural disasters.  
- Azure region pairings generally stay within the same geopolitical boundary except Brazil South which pairs with South Central US.  
- Microsoft uses region pairings for staged rollouts: internal systems → early access → canary → pilot → broader regions → first region in pair → second region in pair.  
- Customers have flexibility and are not forced to use paired regions for their deployments.  
- Azure has a large number of regions worldwide, including West US, West US 2, West US 3, West Central, Canada Central, etc.

**Examples**  
- PowerShell command `Get-AzEnvironment` shows different clouds/environments: Azure Commercial, Azure US Gov, Azure China.  
- Map example showing multiple regions like West US, West US 2, West US 3, Canada Central, with availability zones indicated.  
- Brazil South region pairs with South Central US region, an exception to the geopolitical boundary pairing rule.

**Key Takeaways 🎯**  
- Understand that Azure is not a single cloud but multiple clouds/environments with separate tenants and control planes.  
- Always deploy resources into regions and consider availability zones for resiliency.  
- Use zone-redundant deployments when possible to span multiple availability zones within a region.  
- Choose at least two regions spaced far apart to protect against regional disasters.  
- Region pairings help Microsoft safely roll out updates but customers can choose their own region strategy.  
- Consider latency and data sovereignty when selecting regions for deployment.  
- Subscriptions are tied to tenants and are the scope where resources are deployed.
### 🎤 [01:38:41 – 01:41:35] Azure DNS  
**Timestamp**: 01:38:41 – 01:41:35

**Key Concepts**  
- Azure DNS provides both public and private DNS capabilities.  
- DNS is essential because humans cannot easily remember IP addresses; DNS provides friendly names for resources.  
- Public DNS zones manage records accessible over the Internet.  
- Private DNS zones manage records accessible only within private networks (e.g., virtual networks).  
- Alias records in Azure DNS point directly to Azure resources, preventing dangling DNS issues.  
- Dangling DNS occurs when a DNS record points to a deleted or non-existent resource, which can be exploited by attackers.  
- Azure Traffic Manager creates public DNS records but is typically referenced via custom domain DNS records rather than directly.  
- Private DNS zones can have manual and automatic record creation and can be associated with virtual networks.

**Definitions**  
- **Azure DNS**: A service that provides DNS hosting for both public and private DNS zones within Azure.  
- **Public DNS Zone**: A DNS zone accessible over the Internet, used to manage DNS records for public-facing resources.  
- **Private DNS Zone**: A DNS zone accessible only within specified virtual networks, used for internal name resolution.  
- **Alias Record**: A DNS record type in Azure DNS that points directly to an Azure resource, automatically updating or becoming empty if the resource is deleted, preventing dangling DNS.  
- **Dangling DNS**: A DNS record that points to a resource that no longer exists, which can be hijacked by attackers creating a resource with the same name.

**Key Facts**  
- Azure DNS supports various record types including A, CNAME, MX, and alias records (with some limitations on alias record types).  
- Alias records cannot be created for all record types (e.g., MX records cannot be alias records).  
- When an Azure resource pointed to by an alias record is deleted, the alias record becomes empty and unusable, mitigating security risks.  
- Private DNS zones support automatic record creation and can be linked to virtual networks for seamless internal DNS resolution.

**Examples**  
- Creating an alias record that points to an Azure resource ensures that if the resource is deleted, the DNS record does not become a dangling DNS entry.  
- A dangling DNS scenario described: if a resource is deleted but the DNS record remains, an attacker could create a resource with the same name and hijack traffic.  
- Using a custom domain DNS record to point to Azure Traffic Manager rather than pointing directly to Traffic Manager’s DNS record.

**Key Takeaways 🎯**  
- Use Azure DNS to manage both public and private DNS needs within Azure environments.  
- Prefer alias records for Azure resources to avoid dangling DNS and potential security risks.  
- Understand the difference between public and private DNS zones and their appropriate use cases.  
- Associate private DNS zones with virtual networks to enable automatic internal DNS resolution.  
- When using Azure Traffic Manager, use custom domain DNS records to reference it rather than direct DNS entries.
### 🎤 [01:41:35 – 01:46:51] Azure Private DNS  
**Timestamp**: 01:41:35 – 01:46:51

**Key Concepts**  
- Azure Private DNS zones provide private, internal DNS resolution within virtual networks (VNets).  
- Private DNS zones can have manual and automatic DNS record creation.  
- Auto-registration allows resources in VNets to automatically register DNS records in a private DNS zone.  
- Private DNS zones can be associated with multiple VNets for registration and resolution purposes.  
- Azure Private DNS resolver enables DNS resolution from on-premises or outside VNets to private DNS zones.  
- Default DNS zones exist per VNet but cannot be manually modified.  
- Custom DNS servers can be configured at the VNet level and integrated with Azure Private DNS.  
- Split-brain DNS scenarios are supported by using both public and private DNS zones for the same domain names.

**Definitions**  
- **Private DNS Zone**: A DNS zone accessible only within specified VNets, used for internal name resolution.  
- **Auto Registration**: A feature where resources in a VNet automatically create DNS records in an associated private DNS zone.  
- **Azure Private DNS Resolver**: A managed service that allows DNS queries from outside VNets (e.g., on-premises) to resolve private DNS zone records and can forward queries to custom DNS servers.  
- **Default DNS Zone**: A built-in DNS zone per VNet (e.g., *.internal.cloudapp.net) that cannot be manually edited but provides default internal DNS resolution.  
- **Split Brain DNS**: A DNS configuration where the same domain name resolves differently internally (private DNS zone) and externally (public DNS zone).

**Key Facts**  
- A virtual network can auto-register to only one private DNS zone.  
- A private DNS zone can be used by up to 100 VNets for auto-registration.  
- A virtual network can resolve DNS records from up to 1000 private DNS zones.  
- A private DNS zone can be linked to up to 1000 VNets for resolution purposes.  
- Azure DNS IP address for resolution is always 168.63.129.16, accessible only from within VNets.  
- Azure Private DNS zones are global and can be linked across subscriptions and tenants with appropriate permissions.

**Examples**  
- When a resource is created and auto-registration is enabled, it automatically creates a DNS record in the private DNS zone for internal resolution.  
- Using custom DNS servers at the VNet level requires consideration of forwarding rules to ensure proper resolution, especially when using private link and auto-registration.

**Key Takeaways 🎯**  
- Azure Private DNS zones enable secure, scalable internal DNS resolution across multiple VNets.  
- Auto-registration simplifies DNS management by automatically creating records for resources.  
- The Azure Private DNS resolver bridges DNS queries from on-premises or external networks to private DNS zones.  
- Proper configuration of custom DNS servers and forwarding is critical to maintain resolution functionality.  
- Split brain DNS allows different DNS responses internally and externally, supporting hybrid environments.  
- Understanding limits on associations (100 VNets for registration, 1000 for resolution) is important for large-scale deployments.
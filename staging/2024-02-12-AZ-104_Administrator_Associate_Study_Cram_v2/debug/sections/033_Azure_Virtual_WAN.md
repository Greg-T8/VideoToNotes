### 🎤 [01:56:09 – 01:58:36] Azure Virtual WAN  
**Timestamp**: 01:56:09 – 01:58:36

**Key Concepts**  
- Azure Virtual WAN simplifies complex network connectivity by managing gateways and hub networks centrally.  
- Two SKUs available: Basic and Standard, each supporting different connectivity features.  
- Basic SKU supports site-to-site VPN only.  
- Standard SKU supports site-to-site VPN, ExpressRoute, transitive communication between VNets, and connectivity between multiple Virtual WANs (typically regional).  
- Standard SKU allows deployment of Azure Firewall and custom network virtual appliances within the Virtual WAN.  
- Routing in Virtual WAN can be controlled and overridden using User Defined Routes (UDRs).  

**Definitions**  
- **Azure Virtual WAN**: A managed service that centralizes and simplifies the creation and management of network connectivity, including VPNs, ExpressRoute, and VNet interconnectivity.  
- **Basic SKU**: Azure Virtual WAN option focused solely on site-to-site VPN connectivity.  
- **Standard SKU**: Azure Virtual WAN option that supports site-to-site VPN, ExpressRoute, user point-to-site VPN, intra-hub and VNet-to-VNet transitive routing, and integration with Azure Firewall and network virtual appliances.  
- **User Defined Routes (UDRs)**: Custom routing rules that override default routing policies to direct traffic to specific next hops such as Azure Firewall or network virtual appliances.  

**Key Facts**  
- Basic SKU = site-to-site VPN only.  
- Standard SKU = site-to-site VPN + ExpressRoute + user point-to-site + transitive routing between VNets and hubs + ability to connect multiple Virtual WANs.  
- Standard SKU supports deploying Azure Firewall and custom network virtual appliances inside the Virtual WAN.  
- Azure Virtual WAN is consumption-based; pricing depends on usage and SKU choice.  
- UDRs allow specifying next hop IP addresses for targeted IP spaces, enabling traffic routing through firewalls or appliances.  

**Examples**  
- Using UDRs to route traffic to an Azure Firewall’s private IP address by linking the UDR to a subnet.  

**Key Takeaways 🎯**  
- Azure Virtual WAN is designed to offload and simplify complex network connectivity tasks.  
- Choose Basic SKU for simple site-to-site VPN needs; choose Standard SKU for richer, more integrated connectivity scenarios including ExpressRoute and firewall integration.  
- Standard SKU is the typical choice for most enterprise environments due to its advanced features.  
- UDRs are essential for customizing traffic flow, such as forcing traffic through Azure Firewall or other network appliances.  
- Azure’s consumption-based pricing model means you pay according to the features and scale you use.
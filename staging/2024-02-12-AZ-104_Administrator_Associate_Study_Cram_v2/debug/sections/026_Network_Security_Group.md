### 🎤 [01:28:47 – 01:36:27] Network Security Group  
**Timestamp**: 01:28:47 – 01:36:27

**Key Concepts**  
- Network Security Groups (NSGs) are sets of rules that control inbound and outbound traffic to Azure resources.  
- NSG rules are based on attributes such as priority, name, source, destination, ports, and action (allow or deny).  
- Sources and destinations in NSG rules can be IP addresses, service tags, or application security groups.  
- Service tags represent groups of IP address ranges for Azure services and can simplify rule management.  
- Application Security Groups (ASGs) are tags assigned to NICs to group resources logically for easier NSG rule application.  
- NSGs must be created in the same Azure region as the virtual network (VNet) they are associated with.  
- NSGs have default rules with priorities ranging from 1 (highest) to 65,500 (lowest).  
- NSGs can be associated with subnets or individual NICs.  
- Effective routes and rules impacting a NIC can be viewed to understand traffic flow and restrictions.  
- Azure Firewall is a Microsoft Network Virtual Appliance that can complement NSGs by providing advanced inbound/outbound filtering and NAT capabilities.

**Definitions**  
- **Network Security Group (NSG)**: A collection of security rules that allow or deny inbound and outbound network traffic to Azure resources.  
- **Service Tag**: A label representing a group of IP address prefixes for specific Azure services, used to simplify NSG rule management.  
- **Application Security Group (ASG)**: A logical grouping of NICs that allows NSG rules to be applied based on application roles rather than IP addresses.  
- **Priority (in NSG rules)**: A numeric value determining the order of rule evaluation; lower numbers have higher priority.  
- **Azure Firewall**: A managed, first-party network virtual appliance that provides advanced filtering, NAT, and traffic inspection capabilities.

**Key Facts**  
- NSG rule priority ranges from 1 (highest) to 65,500 (lowest).  
- Default NSG rules allow all traffic within the virtual network and outbound internet traffic, and deny other inbound traffic by default.  
- Service tags include options like "Internet," "AzureLoadBalancer," and region-specific Azure services.  
- Application Security Groups must be in the same region as the NSG.  
- NSGs can filter traffic by protocol (TCP/UDP), port, source, and destination.  
- Effective routes for a NIC show how traffic is routed, including peering and user-defined routes.

**Examples**  
- Blocking inbound TCP port 80 traffic while allowing Azure Load Balancer probes and virtual network traffic.  
- Using an ASG to tag all SQL databases and another ASG for web front ends, then creating NSG rules allowing web front ends to communicate with SQL databases on port 1433 without managing IP addresses.  
- Viewing effective inbound port rules and routes on a virtual machine’s NIC to understand applied security and routing.

**Key Takeaways 🎯**  
- NSGs provide granular control over network traffic using prioritized rules based on source, destination, ports, and protocols.  
- Using service tags and application security groups simplifies management by abstracting IP addresses and grouping resources logically.  
- Always create NSGs in the same region as the VNet they protect.  
- Default NSG rules provide a baseline security posture but can be customized with higher priority rules.  
- Application Security Groups enable flexible, scalable security policies aligned with application roles rather than static IPs.  
- Understanding effective routes and applied rules on NICs helps troubleshoot and verify network security configurations.  
- Azure Firewall can be used alongside NSGs for more advanced network filtering and NAT capabilities.
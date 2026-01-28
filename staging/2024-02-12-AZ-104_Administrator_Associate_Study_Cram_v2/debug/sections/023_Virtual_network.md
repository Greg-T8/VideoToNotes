### 🎤 [01:10:15 – 01:20:00] Virtual network  
**Timestamp**: 01:10:15 – 01:20:00

**Key Concepts**  
- Virtual Network (VNet) is the fundamental building block of Azure networking.  
- A VNet exists within a single Azure subscription and region (cannot span multiple subscriptions or regions).  
- VNets are defined by one or more IPv4 CIDR ranges, commonly private IP ranges (RFC 1918), but can also include custom or public IP ranges (with limitations).  
- VNets are subdivided into subnets, which are subsets of the VNet’s IP address space.  
- Subnets are regional resources and can span multiple Availability Zones within the same region.  
- Each subnet loses 5 IP addresses due to reserved addresses for network, broadcast, gateway, and DNS purposes.  
- Resources connect to VNets via virtual NICs that receive private IP addresses allocated by Azure DHCP.  
- Public IP addresses can be associated with resources for internet accessibility, but private IPs are not internet routable by default.  
- Public IPs come in Standard and Basic SKUs; Standard is recommended as Basic is being retired by September 2025.  
- Azure supports bringing your own public IP prefixes (ranges) with specific size requirements and validation processes.  
- For outbound internet access, explicit configuration is required (e.g., public IP, NAT gateway, Azure Firewall, or Standard Load Balancer with outbound rules) as implicit internet access is being deprecated.  

**Definitions**  
- **Virtual Network (VNet)**: A logically isolated network in Azure that provides IP address space and subnetting within a specific subscription and region.  
- **Subnet**: A subdivision of a VNet’s IP address range, used to organize and isolate resources within the VNet.  
- **CIDR (Classless Inter-Domain Routing)**: A method for allocating IP addresses and IP routing.  
- **Public IP Address**: An IP address reachable from the internet, which can be associated with Azure resources for inbound/outbound connectivity.  
- **Standard SKU Public IP**: A static, highly available public IP address recommended for use in Azure.  
- **Basic SKU Public IP**: A legacy SKU for public IPs that can be dynamic; being retired by September 2025.  
- **NAT Gateway**: A resource that provides outbound internet connectivity for resources in a subnet, efficiently managing port allocation for SNAT.  
- **Azure Firewall**: A managed network security service that can control outbound and inbound traffic with user-defined routes.  
- **Virtual NIC**: A virtual network interface card attached to a resource, which receives an IP address from the subnet’s address space.  

**Key Facts**  
- VNets cannot span multiple subscriptions or regions.  
- Common private IP ranges used: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 (RFC 1918).  
- Each subnet loses 5 IP addresses: network address (.0), broadcast address (.255 for /24), gateway (.1), and two DNS addresses (.2 and .3).  
- Public IP prefixes brought into Azure must be between /21 and /24 for IPv4, and /48 for IPv6.  
- Basic SKU public IPs will be retired on September 3, 2025; Standard SKU is preferred.  
- Subnets are regional and can span all Availability Zones in that region.  
- DHCP is used internally by Azure to assign IPs; users cannot run their own DHCP servers in VNets.  
- Static private IP assignment is possible by reserving an IP for a resource via Azure Fabric.  
- Implicit outbound internet access from VNets is being deprecated; explicit configuration is required for internet connectivity.  

**Examples**  
- VNet named "VNet1" defined with one or more IPv4 CIDR ranges.  
- Subnets labeled subnet1, subnet2, subnet3, subnet4 as subsets of the VNet IP space.  
- Assigning a public IP directly to a resource’s network configuration (not recommended for high availability).  
- Using a Standard Load Balancer with backend pools for resilient internet-facing services.  
- Associating a NAT gateway at the subnet level to provide outbound internet connectivity.  

**Key Takeaways 🎯**  
- Always design VNets within a single subscription and region boundary.  
- Choose unique IP address spaces for VNets and subnets to avoid routing conflicts, especially when connecting to on-premises or other VNets.  
- Remember the 5 reserved IP addresses per subnet when planning IP allocation.  
- Use Standard SKU public IPs for internet-facing resources to ensure static and supported IPs.  
- Plan for explicit outbound internet connectivity configurations as implicit access is being phased out.  
- Consider using NAT gateways or Azure Firewall for efficient and secure outbound internet access rather than assigning public IPs directly to resources.  
- Bringing your own public IP prefixes is possible but involves a complex validation and provisioning process.  
- Subnets are regional and can span multiple Availability Zones, providing flexibility in resource placement.
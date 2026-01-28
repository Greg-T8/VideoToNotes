### 🎤 [01:20:00 – 01:24:36] Peering  
**Timestamp**: 01:20:00 – 01:24:36

**Key Concepts**  
- Virtual Network (VNet) peering allows private IP communication between VNets.  
- Peering can be within the same region or across different regions (inter-region).  
- Peering enables VNets in different subscriptions or regions to communicate without using public endpoints.  
- Hub-and-spoke network topology: a central hub VNet with gateway connectivity and multiple spoke VNets peered to it.  
- Gateway transit allows spoke VNets to use the hub VNet’s gateway for connectivity (e.g., site-to-site VPN, ExpressRoute).  
- Peering relationships are not transitive by default; spokes cannot communicate with each other unless explicitly peered or routed through a network virtual appliance (NVA) like Azure Firewall.  
- User Defined Routes (UDRs) can be used to direct traffic through NVAs to enable transitive routing between VNets.  
- Azure Virtual Network Manager can help manage and configure network groups and peerings at scale.

**Definitions**  
- **VNet Peering**: A connection between two Azure VNets that enables resources in either VNet to communicate with each other privately using private IP addresses.  
- **Gateway Transit**: A peering configuration that allows a spoke VNet to use the gateway (VPN or ExpressRoute) of a hub VNet.  
- **Remote Gateway**: The setting on a spoke VNet peering that allows it to use the gateway of the peered hub VNet.  
- **User Defined Routes (UDRs)**: Custom routing rules that specify next hops for traffic, used to direct traffic through NVAs or firewalls.  
- **Network Virtual Appliance (NVA)**: A virtual appliance (e.g., Azure Firewall) used to manage or inspect network traffic between VNets.  
- **Azure Virtual Network Manager**: A service to centrally manage and configure network groups and peerings across multiple VNets.

**Key Facts**  
- VNets are bound to a specific Azure region and subscription.  
- Peering supports both intra-region and inter-region connections.  
- Gateway transit requires two settings:  
  - On the hub VNet peering: allow gateway transit (or equivalent updated terminology).  
  - On the spoke VNet peering: allow use of remote gateway.  
- Peering connections are not transitive by default; explicit peering or routing is required for spoke-to-spoke communication.  
- Transitive routing can be enabled by routing traffic through an Azure Firewall or other NVA using UDRs.

**Examples**  
- Hub VNet contains a gateway (site-to-site VPN or ExpressRoute).  
- Spoke VNets peer with the hub and are configured to use the hub’s gateway via gateway transit and remote gateway settings.  
- To enable spoke-to-spoke communication, either add direct peering between spokes or route traffic through an Azure Firewall acting as an NVA.  
- Use UDRs to direct traffic from one spoke to another via the Azure Firewall.

**Key Takeaways 🎯**  
- VNet peering enables private, low-latency connectivity between VNets across regions and subscriptions without public internet exposure.  
- Proper configuration of gateway transit and remote gateway settings is essential for spokes to leverage the hub’s gateway connectivity.  
- Peering is not transitive; to enable spoke-to-spoke communication, explicit peering or routing through an NVA is required.  
- NVAs like Azure Firewall combined with UDRs can enable complex routing scenarios including transitive connectivity.  
- Azure Virtual Network Manager can simplify management of multiple peerings and network groups at scale.
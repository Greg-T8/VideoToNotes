### 🎤 [01:58:36 – 01:59:55] User Defined Routes  
**Timestamp**: 01:58:36 – 01:59:55

**Key Concepts**  
- Virtual networks have default routing based on gateways and services like Azure Route Server.  
- User Defined Routes (UDRs) allow overriding these default routes to customize traffic flow.  
- UDRs specify the next hop for specific IP address spaces, directing traffic to chosen network appliances or services.  
- UDRs are linked to subnets to enforce routing policies at that subnet level.  

**Definitions**  
- **User Defined Route (UDR)**: A custom route created to override the default routing behavior in an Azure virtual network by specifying a next hop IP address or service for particular IP address ranges.  

**Key Facts**  
- Default routes are learned automatically based on gateways and Azure Route Server integration.  
- UDRs enable directing traffic to virtual appliances such as Azure Firewall using their private IP addresses.  
- UDRs are applied at the subnet level by associating the route table containing the UDR with the subnet.  

**Examples**  
- To send traffic to an Azure Firewall, create a UDR that points the next hop for a target IP space to the private IP address of the Azure Firewall virtual appliance.  
- Linking the UDR to the subnet ensures all traffic from that subnet follows the defined route to the firewall.  

**Key Takeaways 🎯**  
- Use UDRs when you need to control or modify how traffic flows within your Azure virtual network beyond the default routing.  
- UDRs are essential for directing traffic through security appliances like Azure Firewall.  
- Always associate UDRs with the appropriate subnet to enforce the routing changes.  
- UDRs provide flexibility to integrate custom network virtual appliances into your routing architecture.  

---
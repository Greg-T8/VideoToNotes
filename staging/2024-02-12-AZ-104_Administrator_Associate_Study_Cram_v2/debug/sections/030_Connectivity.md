### 🎤 [01:46:51 – 01:47:52] Connectivity  
**Timestamp**: 01:46:51 – 01:47:52

**Key Concepts**  
- Use of private and public DNS zones for different resolution scopes (internal vs internet)  
- Internet egress requires explicit configuration in Azure gateways/firewalls (default egress is deprecated)  
- Virtual Network (VNet) subnet sizing considerations for gateway subnets  
- VPN gateway types: policy-based (static routing) vs route-based (dynamic routing)  

**Definitions**  
- **Private DNS Zone**: A DNS zone used internally within Azure for private name resolution, isolated from the public internet.  
- **Public DNS Zone**: A DNS zone published to the internet for public name resolution.  
- **Gateway Subnet**: A subnet within a VNet dedicated to hosting VPN gateways or ExpressRoute gateways.  
- **Policy-based VPN**: A VPN type using static routing, limited to one tunnel, considered legacy and not recommended.  
- **Route-based VPN**: A VPN type using dynamic routing, supports multiple tunnels, and is the preferred modern approach.  

**Key Facts**  
- Gateway subnet minimum size: /29 (8 IP addresses)  
- Recommended gateway subnet size: /27 (32 IP addresses) to allow coexistence of site-to-site VPN and ExpressRoute  
- Policy-based VPN supports only one tunnel and requires basic SKU gateways  
- Route-based VPN supports multiple tunnels and is the standard for current Azure VPN gateways  

**Examples**  
- Splitting DNS resolution between a public Azure DNS zone (for internet-facing resources) and a private DNS zone (for internal resolution)  
- Drawing a VNet with a gateway subnet sized /27 to support both site-to-site VPN and ExpressRoute coexistence  

**Key Takeaways 🎯**  
- Plan DNS zones carefully to separate internal and external name resolution using private and public zones  
- Default internet egress from VNets is deprecated; explicit egress configuration is required via gateways or firewalls  
- Allocate sufficient IP space for gateway subnets (preferably /27) to support multiple connectivity options  
- Avoid policy-based VPNs due to limitations and legacy status; prefer route-based VPNs for flexibility and scalability  

---
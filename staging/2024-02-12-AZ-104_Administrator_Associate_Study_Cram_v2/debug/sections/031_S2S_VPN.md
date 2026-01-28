### 🎤 [01:47:52 – 01:50:34] S2S VPN  
**Timestamp**: 01:47:52 – 01:50:34

**Key Concepts**  
- Site-to-site (S2S) VPN connects private IP spaces over the Internet.  
- Two main VPN types: policy-based (static routing) and route-based (dynamic routing).  
- Route-based VPNs support multiple tunnels and point-to-site VPN connections.  
- VPN gateways can be configured in active-passive or active-active modes for redundancy.  
- S2S VPN traffic is encrypted but traverses the public Internet, which may cause variable latency.  
- ExpressRoute is an alternative private connectivity option using Microsoft’s global backbone network.

**Definitions**  
- **Policy-based VPN**: A VPN using static routing, limited to one tunnel, considered legacy and restrictive.  
- **Route-based VPN**: A VPN using dynamic routing, supports multiple tunnels and point-to-site connections, preferred in modern setups.  
- **Active-active VPN gateway**: Configuration where multiple VPN gateways are active simultaneously for redundancy.  
- **Active-passive VPN gateway**: Configuration where one VPN gateway is active and the other is standby.  
- **Point-to-site VPN**: Allows individual computers to connect securely to the VPN gateway.  
- **ExpressRoute**: A private connection option that uses Microsoft’s global network backbone instead of the public Internet.

**Key Facts**  
- Minimum gateway subnet size is /29; recommended size is /27 for coexistence with S2S VPN and ExpressRoute.  
- Policy-based VPNs are only supported on basic SKU gateways and often require PowerShell or Azure CLI to create.  
- Route-based VPNs allow multiple tunnels and are the standard choice.  
- VPN traffic is encrypted but subject to Internet latency variability.  
- Microsoft’s global network includes regional gateways and peering points (“meet me’s”) for ExpressRoute connectivity.

**Examples**  
- Setting a gateway subnet with a /27 mask to allow coexistence of S2S VPN and ExpressRoute.  
- Using route-based VPN to establish multiple tunnels and enable point-to-site VPN for individual clients.  
- Configuring VPN gateways in active-active mode for redundancy on the customer side.

**Key Takeaways 🎯**  
- Prefer route-based VPNs over policy-based due to flexibility and modern support.  
- Plan gateway subnet size (/27 recommended) to support multiple connectivity options.  
- Use active-active or active-passive configurations to increase VPN resilience.  
- Understand that S2S VPNs use encrypted Internet connections, which may impact latency.  
- Consider ExpressRoute for private, more reliable connectivity over Microsoft’s backbone network.
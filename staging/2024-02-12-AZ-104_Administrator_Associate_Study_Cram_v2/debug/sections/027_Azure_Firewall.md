### 🎤 [01:36:27 – 01:38:41] Azure Firewall  
**Timestamp**: 01:36:27 – 01:38:41

**Key Concepts**  
- Azure Firewall is a first-party Microsoft Network Virtual Appliance used for network traffic filtering and control.  
- It supports defining rules for both inbound and outbound traffic.  
- Rules can be applied at different OSI layers: Layer 4 (network layer) and Layer 7 (application layer).  
- Azure Firewall comes in different SKUs: Basic, Standard, and Premium, each with varying performance and features.  
- User Defined Routes (UDRs) are used to direct traffic through the Azure Firewall from different parts of the network.

**Definitions**  
- **Azure Firewall**: A managed, cloud-based network security service that protects Azure Virtual Network resources by filtering traffic using defined rules.  
- **SNAT (Source Network Address Translation)**: Used by Azure Firewall for outbound traffic to translate private IP addresses to public IP addresses.  
- **DNAT (Destination Network Address Translation)**: Used for inbound traffic to translate public IP addresses to private IP addresses.  
- **Layer 4 Rules**: Network layer rules that filter traffic based on TCP/UDP protocols and ports.  
- **Layer 7 Rules**: Application layer rules that filter traffic based on application-level data such as URLs.  
- **SKU (Stock Keeping Unit)**: Different versions of Azure Firewall offering varying performance and features.

**Key Facts**  
- Basic SKU offers low performance.  
- Standard SKU supports up to 30 Gbps throughput.  
- Premium SKU supports up to 100 Gbps throughput.  
- Standard and Premium SKUs support filtering based on categories and can act as a DNS proxy.  
- Premium SKU additionally supports inbound and outbound TLS termination, fully managed intrusion detection and prevention system (IDPS), URL filtering, and SSL termination.  
- Azure Firewall features vary by SKU, so selection depends on required functionality.

**Examples**  
- None explicitly mentioned beyond general capabilities (e.g., inbound/outbound SNAT and DNAT, layer 4 and layer 7 rules).

**Key Takeaways 🎯**  
- Azure Firewall is a versatile, managed firewall solution integrated into Azure networking.  
- Choose the SKU based on required throughput and advanced features like TLS termination and intrusion prevention.  
- Use User Defined Routes to ensure traffic is routed through the Azure Firewall for inspection and filtering.  
- Azure Firewall supports both network-level and application-level filtering, making it suitable for complex security scenarios.
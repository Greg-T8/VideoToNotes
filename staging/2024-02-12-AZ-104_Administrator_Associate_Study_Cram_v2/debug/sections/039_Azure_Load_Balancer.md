### 🎤 [02:12:03 – 02:18:13] Azure Load Balancer  
**Timestamp**: 02:12:03 – 02:18:13

**Key Concepts**  
- Azure Load Balancer operates at Layer 4 (Transport Layer), handling TCP and UDP traffic.  
- It uses front-end IP addresses which can be either internal or external.  
- Back-end pools contain the target resources (NICs or IP addresses) that receive balanced traffic.  
- Health probes monitor the availability of back-end pool instances.  
- Load balancing rules define how traffic is distributed based on tuples (5-tuple, 3-tuple, 2-tuple).  
- NAT rules can be configured for specific traffic redirection.  
- Two SKUs exist: Basic (free) and Standard (paid), with different capabilities and SLAs.  
- Floating IP allows the back-end resource to see the front-end IP instead of its own IP.  

**Definitions**  
- **Azure Load Balancer**: A Layer 4 load balancing service in Azure that distributes incoming TCP/UDP traffic across multiple back-end resources.  
- **Front-end IP**: The IP address exposed by the load balancer to receive incoming traffic; can be internal or external.  
- **Back-end Pool**: A group of IP addresses or NICs that receive traffic from the load balancer.  
- **Health Probe**: A mechanism to check the health and availability of back-end pool members.  
- **Load Balancing Rule**: Configuration that maps incoming traffic to back-end pool members based on matching tuples.  
- **Tuples**: Sets of parameters used to define traffic matching rules:  
  - 5-tuple: destination IP, source IP, destination port, source port, protocol  
  - 3-tuple: destination IP, source IP, protocol  
  - 2-tuple: destination IP, source IP (ignores protocol)  
- **Floating IP**: A rule where the back-end resource sees the front-end IP address as the source IP, avoiding IP rewriting.  
- **Basic SKU (Free)**: Older SKU with limited scale (up to 300 back-end instances), no SLA, and being deprecated by September 30, 2025.  
- **Standard SKU**: Modern SKU supporting up to 1000 back-end instances, availability zones, SLA-backed, requires resources in the same VNet, and supports both NICs and IP addresses in back-end pools.  

**Key Facts**  
- Basic SKU supports up to ~300 back-end instances; no SLA; deprecated and retiring on September 30, 2025.  
- Standard SKU supports up to 1000 back-end instances.  
- Load balancer and back-end resources must be in the same virtual network (no cross-VNet load balancing).  
- Standard SKU supports availability zones and has an SLA.  
- Public IP addresses must match the SKU of the load balancer (Standard with Standard, Basic with Basic).  
- Standard SKU public IPs are locked down by default; outbound rules must be explicitly added for internet access.  
- Basic SKU only supports NICs in back-end pools; Standard SKU supports both NICs and IP addresses (useful for AKS pods which have IP addresses but no NICs).  
- Health probes can be TCP, HTTP, or HTTPS for Standard SKU.  
- Floating IP rules preserve the front-end IP address in traffic sent to back-end resources.  

**Examples**  
- AKS pods can be part of the back-end pool using their IP addresses (Standard SKU).  
- Floating IP useful to avoid IP rewriting in certain communication scenarios.  

**Key Takeaways 🎯**  
- Use Standard SKU for production workloads due to scale, SLA, and feature support; Basic SKU is deprecated.  
- Load balancer front-end IP can be internal or external, but only one type per load balancer instance.  
- Understand tuple-based rules to control session persistence ("stickiness") to back-end pool members.  
- Standard SKU requires back-end resources to be in the same VNet as the load balancer.  
- Floating IP rules are important when you want back-end resources to see the original front-end IP.  
- For web-based applications requiring Layer 7 features, prefer Azure Application Gateway over Azure Load Balancer.  
- Recent updates allow disabling public IP on load balancer front-end and optionally using private IPs.
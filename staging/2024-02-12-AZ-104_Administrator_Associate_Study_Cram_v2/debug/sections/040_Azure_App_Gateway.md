### 🎤 [02:18:13 – 02:25:01] Azure App Gateway  
**Timestamp**: 02:18:13 – 02:25:01

**Key Concepts**  
- Azure Application Gateway (App Gateway) is a Layer 7 load balancer focused on HTTP, HTTPS, HTTP2, and WebSocket traffic.  
- It provides richer functionality than a standard Layer 4 load balancer (like Azure Standard Load Balancer).  
- Supports front-end IP configurations that can be public, private, or optionally none (new feature).  
- Deploys into a subnet within a virtual network; recommended subnet size is /24 for scalability.  
- Supports Web Application Firewall (WAF) integration for protection against common web vulnerabilities.  
- Supports URL-based routing, redirection, SSL/TLS termination, session affinity, and header rewriting.  
- Supports dual stack IP addressing (IPv4 and IPv6).  
- Uses listeners to listen on specific ports and apply routing rules.  
- Supports multisite listeners allowing multiple fully qualified domain names (FQDNs) on the same IP and port.  
- Backend pools are flexible and can include VMs, VM scale sets, IP addresses, FQDNs, and app services, including on-premises resources via VPN or ExpressRoute.  
- Health probes monitor backend target availability.  
- App Gateway is regional; for global load balancing, Azure Traffic Manager (DNS-based) can be used.

**Definitions**  
- **Floating IP**: A feature where the backend pool member sees the frontend IP address instead of its own IP, useful for certain communication scenarios.  
- **Listener**: A configuration on the App Gateway that listens on a specific port and protocol for incoming traffic.  
- **Rule**: Defines how traffic received by a listener is routed to backend pools; can be basic (all traffic to one backend) or path-based.  
- **Web Application Firewall (WAF)**: A security feature integrated with App Gateway that protects against common web vulnerabilities as defined by OWASP.  
- **Multisite Listener**: Allows multiple listeners on the same port differentiated by the hostname (FQDN) in the request, enabling hosting multiple sites on one IP and port.  
- **SSL/TLS Termination**: Offloading the SSL/TLS decryption from backend servers to the App Gateway.

**Key Facts**  
- Previously, App Gateway required a public IP; now public IP is optional and private IP can be used.  
- V2 SKU supports autoscaling and zone redundancy but remains regional.  
- V1 SKU supports up to 32 instances; subnet size recommendations differ accordingly (/26 for V1, /24 recommended for V2).  
- WAF is a paid add-on feature.  
- App Gateway supports session affinity via cookies.  
- Backend pools can include Azure resources or on-premises endpoints via VPN/ExpressRoute or even public IPs.  
- Health probes are used to check backend availability.  
- App Gateway supports both IPv4 and IPv6 (dual stack).  

**Examples**  
- Redirecting HTTP traffic to HTTPS using URL-based routing.  
- Using multisite listeners to host multiple fully qualified domain names on the same IP and port (e.g., multiple sites on port 443).  
- Offloading SSL/TLS termination at the gateway to reduce load on backend servers.  

**Key Takeaways 🎯**  
- Azure App Gateway is ideal for web-based applications needing advanced Layer 7 load balancing features.  
- It offers flexible frontend IP configurations and backend pool targets, including hybrid scenarios.  
- WAF integration enhances security against common web attacks.  
- Multisite listeners and path-based routing enable hosting multiple sites and complex routing rules on a single gateway.  
- SSL/TLS termination and session affinity improve performance and user experience.  
- App Gateway is regional; for global distribution, combine with Azure Traffic Manager.  
- Proper subnet sizing is important for scalability and instance limits.
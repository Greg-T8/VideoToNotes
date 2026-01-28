### 🎤 [02:10:24 – 02:12:03] Load balancing  
**Timestamp**: 02:10:24 – 02:12:03

**Key Concepts**  
- Load balancing is critical for service availability.  
- There are two levels of load balancing: global and regional.  
- Global load balancing provides a single endpoint for clients regardless of resource location.  
- Regional load balancing provides high availability within a region by distributing traffic across multiple instances.  
- Different load balancing solutions apply depending on the service type and network layer.  
- Layer 7 load balancing (application layer) handles HTTP, HTTPS, WebSockets, etc.  
- Layer 4 load balancing (transport layer) handles TCP and UDP traffic.

**Definitions**  
- **Global Load Balancing**: A load balancing approach that provides one endpoint to clients that routes traffic to resources across multiple regions.  
- **Regional Load Balancing**: Load balancing within a single region to distribute traffic among multiple instances for high availability.  
- **Layer 7 Load Balancing**: Load balancing at the application layer, understanding protocols like HTTP and HTTPS. Azure Application Gateway is an example.  
- **Layer 4 Load Balancing**: Load balancing at the transport layer, handling protocols like TCP and UDP. Azure Load Balancer is an example.

**Key Facts**  
- Azure Application Gateway is the Layer 7 load balancing solution.  
- Azure Load Balancer operates at Layer 4.  
- Both global and regional load balancing are necessary for comprehensive availability and scalability.

**Examples**  
- Azure Application Gateway for HTTP/HTTPS and WebSocket traffic (Layer 7).  
- Azure Load Balancer for TCP and UDP traffic (Layer 4).

**Key Takeaways 🎯**  
- Understand the difference between global and regional load balancing and their roles in availability.  
- Choose load balancing solutions based on the network layer and protocol requirements of your service.  
- Use Azure Application Gateway for web-based (Layer 7) traffic.  
- Use Azure Load Balancer for transport layer (Layer 4) traffic such as TCP and UDP.
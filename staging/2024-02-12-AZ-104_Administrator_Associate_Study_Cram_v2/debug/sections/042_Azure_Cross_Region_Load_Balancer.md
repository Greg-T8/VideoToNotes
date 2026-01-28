### 🎤 [02:26:51 – 02:28:09] Azure Cross Region Load Balancer  
**Timestamp**: 02:26:51 – 02:28:09

**Key Concepts**  
- Cross region Load Balancer operates at Layer 4 (transport layer).  
- Provides a global IP address that is public and can route traffic to multiple regional load balancers.  
- Uses anycast IP addressing to direct clients to the closest available regional endpoint.  
- Designed for high availability and resilience both within a region and across regions.  
- Supports global failover: if one region goes down, traffic is routed to another region.  
- Layer 7 global load balancing is handled separately by Azure Front Door.

**Definitions**  
- **Cross Region Load Balancer**: A Layer 4 global load balancing solution in Azure that provides a single public IP address routing traffic to multiple regional load balancers using anycast.  
- **Anycast IP**: An IP addressing method where the same IP is advertised from multiple locations, and client traffic is routed to the nearest or best-performing endpoint.

**Key Facts**  
- The cross region Load Balancer uses a public global IP address.  
- It points to "N" number of regional load balancers (scalable to multiple regions).  
- Microsoft WAN provides the anycast presence and routing.  
- It is primarily a Layer 4 solution for public services.  
- Focus on resilience at all levels: regional and global.

**Examples**  
- None explicitly mentioned, but the concept involves clients connecting to a global IP that routes to the closest regional load balancer.

**Key Takeaways 🎯**  
- Use Azure Cross Region Load Balancer for global Layer 4 load balancing with a single public IP.  
- It ensures high availability by routing traffic to healthy regional endpoints and providing failover across regions.  
- Anycast IP addressing enables clients to connect to the nearest regional load balancer automatically.  
- For Layer 7 global load balancing, Azure Front Door is the recommended service.  
- Important to design for resilience both within regions and globally.
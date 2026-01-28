### 🎤 [03:28:11 – 03:30:54] Availability Set and Zones  
**Timestamp**: 03:28:11 – 03:30:54

**Key Concepts**  
- Azure Bastion provides a secure way to connect to virtual machines without exposing public IPs.  
- A virtual machine runs on a physical host located in a specific rack within a data center.  
- Fault domains represent physical racks or hardware units that can fail independently.  
- Availability Sets group VMs across multiple fault domains (racks) to provide resiliency against rack-level failures.  
- Availability Zones are physically separate locations within an Azure region that isolate power, cooling, networking, and control planes.  
- Availability Zones offer higher fault tolerance than Availability Sets by protecting against entire data center or power substation failures.  

**Definitions**  
- **Azure Bastion**: A managed jump box service that enables secure and seamless RDP/SSH connectivity to VMs without exposing them to the public internet.  
- **Fault Domain**: A logical group of hardware (e.g., a rack) that shares a common power source and network switch, representing a potential point of failure.  
- **Availability Set**: A grouping of VMs that are distributed across multiple fault domains to ensure resiliency against hardware failures within a data center.  
- **Availability Zone**: Physically separate zones within an Azure region, each with independent power, cooling, networking, and control planes, designed to protect against larger-scale failures.  

**Key Facts**  
- Availability Sets distribute VMs across fault domains (e.g., fault domain 0, 1, 2) to avoid single points of failure at the rack level.  
- Workloads should be separated into different availability sets to avoid all instances of one service being placed in the same fault domain.  
- Availability Zones provide protection against failures at the data center or power substation level, offering a larger blast radius protection than Availability Sets.  
- Not all Azure regions support Availability Zones; in those cases, Availability Sets are the fallback option.  

**Examples**  
- Using Availability Sets to round robin VMs across racks (fault domains) to ensure resiliency.  
- Separating different workloads into different availability sets to avoid correlated failures.  
- Deploying VMs across multiple Availability Zones to protect against entire data center failures.  

**Key Takeaways 🎯**  
- Always prefer Availability Zones over Availability Sets when supported, as they provide stronger fault isolation.  
- Use Availability Sets to distribute VMs across fault domains within a data center to protect against rack-level failures.  
- Separate different workloads into distinct availability sets to avoid placing all instances in the same fault domain.  
- Azure Bastion is recommended for secure VM access instead of exposing public IPs.  
- Understand the physical infrastructure behind VMs (racks, fault domains, zones) to design resilient architectures.
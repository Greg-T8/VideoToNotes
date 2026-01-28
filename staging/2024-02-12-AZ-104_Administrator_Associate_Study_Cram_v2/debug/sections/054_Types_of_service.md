### 🎤 [03:15:07 – 03:19:05] Types of service  
**Timestamp**: 03:15:07 – 03:19:05

**Key Concepts**  
- Different levels of responsibility exist depending on the type of cloud service used.  
- Layers involved in computing: storage, network, compute (servers), hypervisor, operating system, runtime, application, and data.  
- On-premises environments require full responsibility for all layers.  
- Cloud services shift responsibility between vendor and user depending on service type.  
- Types of cloud services: Infrastructure as a Service (IaaS), Platform as a Service (PaaS), Software as a Service (SaaS).  
- The goal is to minimize user responsibility to focus on business value rather than infrastructure management.

**Definitions**  
- **Infrastructure as a Service (IaaS)**: Cloud service where the vendor manages physical servers, storage, networking, and hypervisor; the user manages the OS and everything above it (patching, antivirus, backup, disaster recovery, etc.).  
- **Platform as a Service (PaaS)**: Cloud service where the vendor manages infrastructure and platform layers; the user is responsible only for the application and data. Includes managed databases and app hosting platforms.  
- **Software as a Service (SaaS)**: Fully managed cloud applications (e.g., Microsoft 365, Dynamics 365) where the vendor handles all infrastructure, platform, and application maintenance; the user mainly manages identities and access.

**Key Facts**  
- In IaaS, users must handle OS patching, antivirus, backup, disaster recovery, and anti-malware.  
- Azure provides tools like agents and extensions to help manage VMs but responsibility remains with the user.  
- PaaS examples include virtual machine scale sets, Azure Kubernetes Service, app services, and serverless offerings like Azure Functions and Logic Apps.  
- SaaS examples include Microsoft 365 and Dynamics 365, where users do not patch or maintain the underlying services.  
- Users should aim to move as far right (towards SaaS) in the service model as possible to reduce operational overhead.  
- Virtual machines have multiple dimensions such as SKU, size, CPU, and memory.

**Examples**  
- IaaS: Virtual machines in Azure.  
- PaaS: Virtual machine scale sets, Azure Kubernetes Service, app services, Azure Functions, Logic Apps.  
- SaaS: Microsoft 365, Dynamics 365.

**Key Takeaways 🎯**  
- Understanding the division of responsibility is critical when choosing cloud service types.  
- The less responsibility you have for infrastructure and platform management, the more you can focus on your application and business logic.  
- Even though VMs are the foundational service, many higher-level services build on top of them.  
- Use Azure tools to assist with management but remember ultimate responsibility depends on the service model.  
- Aim to leverage PaaS and SaaS offerings to reduce operational burden and increase focus on business value.
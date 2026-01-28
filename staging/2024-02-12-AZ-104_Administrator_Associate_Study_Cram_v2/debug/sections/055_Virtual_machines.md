### 🎤 [03:19:05 – 03:28:11] Virtual machines  
**Timestamp**: 03:19:05 – 03:28:11

**Key Concepts**  
- Virtual machines (VMs) have multiple dimensions or characteristics such as CPU, memory, storage, network capabilities, and GPUs.  
- VM SKUs and sizes define these dimensions and are chosen based on workload requirements.  
- Workloads have different "shapes" (resource needs) that should be matched to the appropriate VM SKU and size to optimize resource use and cost.  
- Scaling is often better achieved by multiple smaller VMs rather than one large VM.  
- Azure offers various VM series optimized for different purposes: general purpose, compute optimized, memory optimized, GPU-enabled, storage optimized, and burstable VMs.  
- Burstable VMs (B series) allow CPU credits to be banked and used for short bursts of higher CPU usage, useful for dev/test or variable workloads.  
- VMs run on physical hosts with local storage; ephemeral OS disks can be used to reduce costs and improve performance when state persistence is not required.  
- Managed disks are typically used for OS and data disks unless ephemeral disks are leveraged.  
- VMs support extensions to add capabilities such as running custom scripts, backup integration, auto shutdown, and disaster recovery.  
- Backup management can be centralized via Azure Backup Center with different vault types (Recovery Services vault for legacy workloads and newer backup vaults for disks, blobs, databases, Kubernetes).  
- Secure access to VMs is recommended via Azure Bastion to avoid exposing public IPs and reduce attack surface.  
- Physical hosts and racks correspond to fault domains within data centers, important for availability considerations.

**Definitions**  
- **SKU (Stock Keeping Unit)**: A specific configuration of a VM defining its CPU, memory, storage, and other capabilities.  
- **Burstable VM (B series)**: A VM type that accumulates CPU credits when underused and allows short bursts of higher CPU usage when needed.  
- **Ephemeral Disk**: A temporary OS disk stored on the local host’s physical storage, offering low latency and high performance but without persistent state.  
- **Azure Bastion**: A managed jump box service that provides secure and seamless RDP/SSH connectivity to VMs without exposing public IP addresses.  
- **Managed Disk**: Azure-managed persistent storage used for VM OS and data disks.  
- **Backup Center**: A centralized Azure service for managing backups across various workloads and vault types.

**Key Facts**  
- General purpose VMs typically have a 1:4 ratio of vCPU to memory.  
- Compute optimized VMs have a 1:2 CPU to memory ratio.  
- Memory optimized VMs have a 1:8 CPU to memory ratio.  
- Some VM series (D variant) include temporary local storage (temp disk), while others (non-D) do not.  
- Premium storage support is available on S variants of VMs, not on standard ones.  
- Burstable VMs allow CPU usage beyond the baseline by using banked credits.  
- Ephemeral OS disks are commonly used in scale sets and AKS node pools to reduce managed disk costs and improve performance.  
- Temporary storage is typically mounted as D: on Windows and /dev/sdb on Linux for D-series VMs.

**Examples**  
- Database workloads typically require high memory and storage throughput.  
- Batch processing workloads typically require high CPU resources.  
- Using multiple smaller VMs instead of one large VM allows better scaling and cost efficiency.  
- Dev/test environments can leverage burstable VMs to minimize costs by using CPU credits.  
- Virtual machine scale sets and AKS node pools often use ephemeral disks for OS to reduce costs and improve latency.  
- Azure Bastion is used to securely connect to VMs without exposing public IPs.

**Key Takeaways 🎯**  
- Understand the resource "shape" of your workload to select the appropriate VM SKU and size.  
- Prefer scaling out with multiple smaller VMs rather than scaling up with a single large VM.  
- Use burstable VMs for workloads with variable CPU demand to save costs.  
- Leverage ephemeral disks where possible for stateless or short-lived VMs to reduce storage costs and improve performance.  
- Use VM extensions to automate management tasks like running scripts, backups, and shutdowns.  
- Centralize backup management using Azure Backup Center and choose the appropriate vault type based on workload.  
- Always secure VM access using Azure Bastion or similar managed jump box solutions to minimize attack surface.  
- Consider physical host and fault domain placement for high availability and fault tolerance planning.
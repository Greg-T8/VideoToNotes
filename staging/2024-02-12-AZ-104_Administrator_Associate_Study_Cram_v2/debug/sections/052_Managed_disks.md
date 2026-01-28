### 🎤 [03:02:54 – 03:10:21] Managed disks  
**Timestamp**: 03:02:54 – 03:10:21

**Key Concepts**  
- Managed disks abstract away the underlying storage account and page blobs from the user.  
- Different types of managed disks exist, each with varying performance and latency characteristics.  
- Disk performance is generally tied to disk capacity; larger disks offer better performance.  
- Some disk types allow dynamic adjustment of IOPS and throughput independent of capacity.  
- Encryption for managed disks can be handled via disk encryption sets using customer-managed keys or via guest OS encryption (Azure Disk Encryption).  
- Encryption at host can be combined with disk encryption sets for enhanced security, including encryption of cache files and data in transit.

**Definitions**  
- **Managed Disk**: A disk resource in Azure that abstracts the underlying storage account and page blob, simplifying management and improving scalability.  
- **Disk Encryption Set**: A resource that associates managed disks with a customer-managed key stored in Azure Key Vault for encryption at rest.  
- **Azure Disk Encryption (ADE)**: Encryption performed inside the guest OS (e.g., BitLocker for Windows, DMcrypt for Linux), with keys stored in Key Vault.  
- **Encryption at Host**: Encryption applied to cache files on the physical host running the VM, encrypting data in transit between disk and host, using platform-managed keys.

**Key Facts**  
- Types of managed disks:  
  - Standard HDD  
  - Standard SSD  
  - Premium SSD  
  - Premium SSD V2  
  - Ultra Disk  
- Latency examples:  
  - Ultra Disk offers ~0.5 millisecond latency (lowest latency).  
  - Premium SSD offers ~1 millisecond latency.  
- Disk performance scales with capacity; bigger disks provide better IOPS and throughput.  
- Premium SSD allows selection of performance tiers to temporarily boost performance without resizing the disk.  
- Disks can only be increased in size; shrinking requires creating a new disk and migrating data.  
- Premium SSD V2 and Ultra Disk allow independent selection and dynamic modification of IOPS and throughput up to defined limits.  
- Standard SSD supports sharing, allowing multiple resources to connect to the same disk.  
- Disk encryption sets use customer-managed keys from Azure Key Vault to encrypt managed disks.  
- Azure Disk Encryption (ADE) encrypts data inside the VM guest OS and also uses Key Vault for key management.  
- Encryption at host encrypts cache files and data in transit between disk and host, enhancing security.  
- Temporary performance boosts can be applied by adjusting IOPS and throughput settings on Premium SSD V2 and Ultra Disk.

**Examples**  
- None explicitly mentioned beyond conceptual scenarios (e.g., using disk encryption sets with customer keys, or guest OS encryption with BitLocker/DMcrypt).

**Key Takeaways 🎯**  
- Managed disks simplify storage management by abstracting storage accounts and page blobs.  
- Choose disk type based on required latency and performance; Ultra Disk offers the best performance.  
- Disk size directly impacts performance; plan capacity carefully since disks cannot be shrunk.  
- Use performance tiers or adjustable IOPS/throughput options to optimize cost and performance dynamically.  
- For encryption, disk encryption sets with customer-managed keys provide flexible and secure encryption at rest.  
- Azure Disk Encryption offers guest-level encryption but may impose management constraints.  
- Combining encryption at host with disk encryption sets provides comprehensive encryption coverage, including data in transit and cache files.  
- Always consider encryption and performance needs when provisioning managed disks to balance security, cost, and efficiency.
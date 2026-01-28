### 🎤 [02:31:50 – 02:42:07] Storage accounts  
**Timestamp**: 02:31:50 – 02:42:07

**Key Concepts**  
- Azure storage accounts are the fundamental building blocks for durable, persistent storage in Azure.  
- Storage accounts live in a specific Azure region and have configurable performance and redundancy options.  
- General Purpose v2 (GPv2) storage accounts are the most commonly used and support blobs, queues, tables, and files.  
- Premium storage options exist, typically service-specific and based on SSD technology, with different billing models.  
- Azure Blob storage supports block blobs (common for multimedia), page blobs (used mainly for disks), and append blobs (for logging scenarios).  
- Azure Files supports SMB and NFS protocols for file shares.  
- Azure Tables provide schemaless key-value storage with partition and row keys.  
- Azure Queues provide FIFO message queuing.  
- Redundancy options determine how many copies of data exist and where they are stored to ensure resiliency.

**Definitions**  
- **Storage Account**: A container in Azure that holds all storage data objects like blobs, files, queues, and tables, scoped to a region with specific performance and redundancy settings.  
- **General Purpose v2 (GPv2)**: The default and most versatile storage account type supporting all storage services with standard performance.  
- **Premium Storage**: Storage backed by SSDs, service-specific, and often billed based on provisioned size rather than actual data usage (notably for premium file shares).  
- **Block Blob**: Blob type optimized for storing large files such as multimedia.  
- **Page Blob**: Blob type optimized for random read/write operations, historically used for disks.  
- **Append Blob**: Blob type optimized for append operations, such as logging.  
- **Locally Redundant Storage (LRS)**: Stores 3 copies of data within a single storage cluster in the same region.  
- **Zone-Redundant Storage (ZRS)**: Stores 3 copies of data spread across availability zones within the same region.  
- **Geo-Redundant Storage (GRS)**: Stores 3 copies in the primary region and asynchronously replicates 3 copies to a paired secondary region (6 copies total).  
- **Geo-Zone-Redundant Storage (GZRS)**: Combines ZRS in the primary region with asynchronous replication to a secondary region (6 copies total).  
- **Read-Access Geo-Redundant Storage (RA-GRS/RA-GZRS)**: Allows read access to the secondary (replica) region for blob data.

**Key Facts**  
- Storage accounts must be named and assigned to a specific Azure region.  
- General Purpose v2 is the recommended and most common storage account type; General Purpose v1 and standard block blob accounts are generally avoided.  
- Premium file shares charge based on provisioned size, not actual data written, because performance scales with provisioned size.  
- Storage Explorer is a powerful tool to interact with storage accounts, allowing viewing and manipulation of blobs, files, queues, and tables.  
- Tables are schemaless, storing key-value pairs with partition and row keys.  
- Redundancy options:  
  - LRS: 3 copies in one cluster  
  - ZRS: 3 copies across availability zones in a region  
  - GRS: 3 copies in primary + 3 copies asynchronously replicated to secondary region  
  - GZRS: ZRS in primary + async replication to secondary region  
- Asynchronous replication means data is acknowledged as stored once in primary region; replication to secondary happens in the background to avoid latency impact.  
- Firewall and network restrictions can be applied to storage accounts (service endpoints, private endpoints).  
- Hierarchical namespace can be enabled for blob storage to support POSIX-style ACLs.

**Examples**  
- Using Storage Explorer to:  
  - View containers and files in a storage account  
  - Add and dequeue messages in a queue  
  - Add schemaless entities to a table with custom properties  
- Explanation of premium file shares billing based on provisioned size, not actual data written.  
- Explanation of redundancy with copies spread across availability zones or paired regions.

**Key Takeaways 🎯**  
- Always use General Purpose v2 storage accounts unless you have a specific premium need.  
- Understand the difference between standard and premium storage, especially billing implications for premium file shares.  
- Choose redundancy options based on your resiliency and availability requirements; higher redundancy means more copies and geographic spread.  
- Use Storage Explorer as a practical tool for managing and interacting with storage accounts.  
- Asynchronous geo-replication ensures durability without impacting application latency.  
- Enable hierarchical namespace if you need POSIX-style ACLs on blob storage.  
- Secure storage accounts with firewall and network restrictions to control access.
### 🎤 [00:04:01 – 00:04:52] AFS in Israel Central  
**Timestamp**: 00:04:01 – 00:04:52

**Key Concepts**  
- Azure File Sync (AFS) enables synchronization of Windows File Server SMB shares via Azure File Shares in the cloud.  
- AFS allows local SMB shares to offload content to the cloud when running out of capacity, providing virtually unlimited storage.  
- Content that is offloaded appears available locally but is actually stored in the cloud and downloaded on-demand, which may cause increased latency.  
- Deploying the sync service in multiple locations reduces latency and helps meet data residency requirements.

**Definitions**  
- **Azure File Sync (AFS)**: A service that synchronizes SMB shares from Windows File Servers to Azure File Shares, enabling cloud-based storage extension and centralized file management.

**Key Facts**  
- Azure File Sync is now available in the Israel Central region.  
- Offloaded content is not stored locally but remains visible to users.  
- Accessing offloaded content triggers on-demand download, which can increase latency.  
- Multi-location sync service deployment reduces lag and supports data residency compliance.

**Examples**  
- A Windows File Server running out of SMB share capacity can offload files to Azure File Share, maintaining the appearance of local availability while freeing local storage.

**Key Takeaways 🎯**  
- Azure File Sync extends local file server storage capacity by leveraging cloud storage transparently.  
- Offloading files helps manage limited local storage but may introduce latency when accessing offloaded files.  
- Deploying sync services closer to users or in required regions improves performance and compliance.  
- Availability of AFS in Israel Central expands options for customers in that geography.
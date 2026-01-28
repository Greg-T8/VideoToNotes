### 🎤 [01:06:56 – 01:09:28] Resource locking  
**Timestamp**: 01:06:56 – 01:09:28

**Key Concepts**  
- Resource locks can be applied at subscription, resource group, or individual resource levels.  
- There are two types of locks: "Cannot delete" and "Read only."  
- Locks affect only the Azure control plane, not the data plane.  
- Locks are inherited down the resource hierarchy.  

**Definitions**  
- **Cannot delete lock**: Prevents deletion of the resource but allows modifications.  
- **Read only lock**: Prevents any modifications, including writes, to the resource.  
- **Control plane**: The management layer of Azure where resources are created, configured, or deleted.  
- **Data plane**: The layer where data operations occur, such as writing or deleting records inside a resource (e.g., database entries, blobs).  

**Key Facts**  
- Locks only restrict actions on the control plane, not on the data plane.  
- Even with a delete lock on a storage account, you can still delete blobs inside it because blob operations happen on the data plane.  
- Locks are inherited from higher levels (subscription/resource group) down to resources.  

**Examples**  
- A "backup protection" lock set to "delete" on a storage account prevents deleting the storage account itself but does not prevent deleting blobs inside it.  
- You can write records to a database or create/delete blobs even if the resource is locked at the control plane level.  

**Key Takeaways 🎯**  
- Resource locks are a control plane feature to prevent accidental deletion or modification of Azure resources.  
- Locks do not protect the data inside resources; data plane operations remain unaffected.  
- Understand the distinction between control plane and data plane when applying locks to avoid false assumptions about data protection.  
- Use locks strategically at appropriate scopes (subscription, resource group, resource) to safeguard critical infrastructure components.
### 🎤 [02:49:05 – 02:50:22] Lifecycle management  
**Timestamp**: 02:49:05 – 02:50:22

**Key Concepts**  
- Lifecycle management automates data tiering based on rules and filters.  
- Rules can move data between access tiers (hot, cool, cold, archive) based on criteria like last access time, creation, or modification date.  
- Lifecycle management can also automate deletion after a certain period.  
- Filters can be based on blob name, BLOB index keys, or other metadata.  
- Automation helps avoid manual and cumbersome tier management.  

**Definitions**  
- **Lifecycle management**: A system to create rules that automatically move or delete data based on access patterns, age, or other filters to optimize storage costs and accessibility.  
- **Access tiers**: Different storage performance and cost levels (e.g., hot, cool, cold, archive) that data can be moved between depending on usage.  

**Key Facts**  
- Example rules:  
  - Move data to cool tier if not accessed for 15 days.  
  - Move data to cold tier if not accessed for 45 days.  
  - Move data to archive tier if not accessed for 135 days.  
- Changing data from archive tier to online tier for access can take hours.  
- Filters for lifecycle rules can include blob name patterns and BLOB index keys.  

**Examples**  
- Created lifecycle rules that move blobs to cool after 15 days of no access, to cold after 45 days, and to archive after 135 days.  

**Key Takeaways 🎯**  
- Automate data tiering with lifecycle management to optimize storage costs and access efficiency.  
- Respect minimum retention times when setting lifecycle rules to avoid premature deletion or tier changes.  
- Use filters like blob names or index keys to target specific data sets for tiering.  
- Manual tier changes, especially from archive, can be time-consuming; automation reduces operational overhead.
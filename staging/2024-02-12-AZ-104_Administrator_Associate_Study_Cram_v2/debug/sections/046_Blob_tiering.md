### 🎤 [02:44:20 – 02:49:05] Blob tiering  
**Timestamp**: 02:44:20 – 02:49:05

**Key Concepts**  
- Blob storage supports tiering to optimize cost based on data access patterns.  
- Four blob tiers available: Hot, Cool, Cold, and Archive.  
- Tiering can be set at the individual blob level.  
- Costs depend on both storage capacity and transaction frequency.  
- Lifecycle management can automate tier transitions and deletions.

**Definitions**  
- **Hot tier**: Highest storage cost but lowest transaction cost; ideal for frequently accessed data.  
- **Cool tier**: Lower storage cost than Hot, higher transaction cost; suitable for infrequently accessed data.  
- **Cold tier**: Even lower storage cost, higher transaction cost; for rarely accessed data that must be instantly available.  
- **Archive tier**: Lowest storage cost, no immediate access; data is offline and requires rehydration (can take 12-13 hours) to access.  

**Key Facts**  
- Storage cost decreases from Hot → Cool → Cold → Archive.  
- Transaction costs increase from Hot → Cool → Cold → Archive (due to retrieval overhead).  
- Archive data must be rehydrated before access, which can take hours.  
- Minimum retention periods apply:  
  - Cool: 30 days  
  - Cold: 90 days  
  - Archive: 180 days  
- Early deletion before minimum retention results in billing for the remaining days.  
- Blob tiering can be mixed within a single container (some blobs Hot, some Cool, Cold, or Archive).  
- Archive blobs cannot be downloaded directly; they must be moved to an online tier first.  
- Cold tier blobs are online and can be downloaded immediately.  

**Examples**  
- A container with mixed tiers: some blobs in Hot (default), some in Cool, Cold, and one in Archive.  
- Archive blob’s download option is disabled (grayed out) because it is offline.  
- Cold tier blobs can be downloaded directly despite higher transaction costs.  

**Key Takeaways 🎯**  
- Choose blob tiers based on access frequency to optimize costs.  
- Remember minimum retention periods to avoid unexpected charges.  
- Use lifecycle management policies to automate tier transitions and deletions based on criteria like last access time or blob name.  
- Archive tier is best for long-term retention when immediate access is not required.  
- Mixing tiers within containers is supported, allowing flexible cost management.  
- Manual tier management is possible but lifecycle management is recommended for efficiency.
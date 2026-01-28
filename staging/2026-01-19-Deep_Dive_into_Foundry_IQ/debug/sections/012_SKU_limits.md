### 🎤 [00:17:09 – 00:17:46] SKU limits  
**Timestamp**: 00:17:09 – 00:17:46

**Key Concepts**  
- Different SKUs (stock keeping units) of Azure AI Search have varying limits on the number of knowledge bases and knowledge sources they support.  
- Knowledge bases are collections of knowledge sources grouped together to represent useful knowledge about enterprise entities or other topics.  
- Once a knowledge source is created, it can be reused across multiple knowledge bases.

**Definitions**  
- **SKU (Stock Keeping Unit)**: A specific version or tier of Azure AI Search service that determines capacity and feature limits.  
- **Knowledge Source**: An individual data source or repository of information that can be added to Azure AI Search.  
- **Knowledge Base**: A collection of one or more knowledge sources grouped to represent a coherent set of information.

**Key Facts**  
- Free SKU supports up to 3 knowledge sources and 3 knowledge bases.  
- Basic SKU supports up to 15 knowledge sources and knowledge bases (with some historical exceptions based on creation date).  
- Higher SKUs like S1, S2, S3 support progressively larger numbers of knowledge sources and knowledge bases (exact numbers not specified in this excerpt).  

**Examples**  
- None explicitly mentioned in this section, but the concept of grouping multiple knowledge sources (e.g., blobs, policies, SharePoint data) into knowledge bases is implied.

**Key Takeaways 🎯**  
- When planning Azure AI Search deployments, choose the SKU based on the number of knowledge sources and knowledge bases needed.  
- Knowledge sources are reusable assets that can be combined flexibly into multiple knowledge bases.  
- Check the official limits page regularly as SKU limits may change over time.
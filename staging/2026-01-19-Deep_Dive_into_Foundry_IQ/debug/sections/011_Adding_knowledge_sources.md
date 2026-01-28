### 🎤 [00:15:44 – 00:17:09] Adding knowledge sources  
**Timestamp**: 00:15:44 – 00:17:09

**Key Concepts**  
- A knowledge base consists of multiple knowledge sources.  
- You can add existing knowledge sources or create new ones.  
- Knowledge sources can be various types of data repositories or indexes.  
- Knowledge sources live within Azure AI Search instances.  
- Different Azure AI Search SKUs support different limits on knowledge bases and knowledge sources.

**Definitions**  
- **Knowledge base**: A collection of knowledge sources.  
- **Knowledge source**: A data repository or index that provides content to be included in a knowledge base (e.g., search indexes, blob storage, SharePoint sites).

**Key Facts**  
- Current example uses 10 knowledge sources, but this number can change.  
- Knowledge sources can be:  
  - Existing search indexes  
  - Blob containers (automatically chunked and indexed)  
  - Web content  
  - SharePoint site indexes (creating an Azure AI Search index)  
  - SharePoint in general (using remote semantic index of M365)  
  - Fabrics OneLake (retrieves data and creates an index)  
- MCP (Microsoft Content Platform) integration is in private preview and not available in the demo.  
- Multiple Azure AI Search resources can be added, each with different knowledge bases.  
- Azure AI Search SKU limits example:  
  - Free SKU supports 3 knowledge sources and 3 knowledge bases.  
  - Basic SKU supports 15 knowledge sources (with some date-related exceptions).  
  - Higher SKUs (S1, S2, S3, etc.) support progressively more knowledge sources and bases.

**Examples**  
- Pointing a knowledge source to a blob container for automatic chunking and indexing.  
- Using a SharePoint site index to create an Azure AI Search index.  
- Using SharePoint with the remote semantic index of M365.  
- Using Fabrics OneLake as a knowledge source.

**Key Takeaways 🎯**  
- Knowledge bases are flexible collections of various knowledge sources.  
- You can reuse existing knowledge sources across knowledge bases.  
- Azure AI Search instances host knowledge sources and knowledge bases.  
- Be aware of SKU limits when planning the number of knowledge sources and knowledge bases.  
- New types of knowledge sources and integrations (like MCP) are evolving and may become available later.
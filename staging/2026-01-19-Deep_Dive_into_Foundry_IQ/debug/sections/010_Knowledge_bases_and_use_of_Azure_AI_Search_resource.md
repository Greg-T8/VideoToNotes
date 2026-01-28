### 🎤 [00:14:22 – 00:15:44] Knowledge bases and use of Azure AI Search resource  
**Timestamp**: 00:14:22 – 00:15:44

**Key Concepts**  
- Azure AI Search resource must be created first before creating knowledge bases.  
- A knowledge base is a collection of one or more knowledge sources.  
- Knowledge sources can include Azure AI Search Index, web, SharePoint site indexes, BLOB containers, etc.  
- Knowledge bases are the primary entities users interact with, sitting above knowledge sources.  
- Users can add existing knowledge sources or create new ones within a knowledge base.  

**Definitions**  
- **Azure AI Search resource**: A prerequisite resource in Azure that enables indexing and searching capabilities.  
- **Knowledge base**: A container or collection of multiple knowledge sources used for search and information retrieval.  
- **Knowledge source**: An individual data source or index (e.g., Azure AI Search Index, web, SharePoint) that feeds into a knowledge base.  

**Key Facts**  
- You can have up to 10 knowledge sources within a single knowledge base (subject to change).  
- Knowledge sources can be reused across multiple knowledge bases.  

**Examples**  
- Two knowledge bases shown: each contains knowledge sources such as an Azure AI Search Index and a web source.  
- Knowledge sources can point to:  
  - Existing Azure AI Search indexes  
  - BLOB containers (documents are chunked and indexed)  
  - Web content  
  - Specific SharePoint site indexes or SharePoint in general  

**Key Takeaways 🎯**  
- Always create an Azure AI Search resource before setting up knowledge bases.  
- Think of knowledge bases as the main interface, composed of multiple knowledge sources.  
- Flexibility to add existing or new knowledge sources allows for diverse data integration.  
- Knowledge sources can be shared and reused, promoting efficient resource management.  
- The current limit of 10 knowledge sources per knowledge base may evolve.
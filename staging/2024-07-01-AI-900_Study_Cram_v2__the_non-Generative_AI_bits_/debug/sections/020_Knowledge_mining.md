### 🎤 [01:06:05 – 01:09:39] Knowledge mining  
**Timestamp**: 01:06:05 – 01:09:39

**Key Concepts**  
- Knowledge mining is the process of extracting insights and relevant information from large volumes of data.  
- Azure AI Search (formerly Azure Cognitive Search) is the primary service used for knowledge mining in Azure.  
- Data sources can include BLOB storage, data lakes, databases, and table storage.  
- Skill sets define how data is processed, including chunking large documents into smaller parts for analysis.  
- Embedding models convert chunks of data into high-dimensional vector representations capturing semantic meaning.  
- Enrichment processes can include calling vision services to extract text from images within documents.  
- Knowledge mining creates both traditional text indexes and vector indexes to support hybrid search capabilities.  
- Hybrid search combines exact phrase matching and semantic vector search to improve query relevance.  

**Definitions**  
- **Knowledge mining**: The process of extracting meaningful insights from large, unstructured or structured data sets using AI-powered search and enrichment techniques.  
- **Azure AI Search**: An Azure resource/service designed to index and search data using both traditional text and semantic vector methods.  
- **Skill sets**: Configurations that define how data is processed and enriched during indexing, such as chunking and calling AI services.  
- **Chunking**: Breaking large documents into smaller overlapping pieces to enable detailed semantic analysis.  
- **Embedding model**: A model that transforms text chunks into vector representations that capture the semantic meaning of the content.  
- **Hybrid search**: A search approach that combines traditional keyword-based search with vector-based semantic search and re-ranks results accordingly.  

**Key Facts**  
- Azure AI Search is a standalone resource, not part of the multi-service Azure AI accounts.  
- Data can come from various sources including BLOB storage, data lakes, databases, and table storage.  
- Chunking involves breaking data into smaller parts with some overlap to preserve context.  
- The service can enrich data by integrating with other AI services, such as vision for OCR on images in PDFs.  
- Both exact text indexes and vector indexes are created to support hybrid search functionality.  
- Hybrid search improves natural language query results by combining phrase matching and semantic understanding.  

**Examples**  
- A large document about "a dog going to the park" is chunked and embedded into vectors representing its semantic content.  
- A query like "information about puppies going to public green areas" can successfully retrieve the document about a dog going to the park due to semantic vector search.  

**Key Takeaways 🎯**  
- Knowledge mining enables extracting actionable insights from large and complex data sets by combining AI enrichment and advanced search techniques.  
- Azure AI Search is the core Azure service for knowledge mining, supporting both traditional and semantic search indexes.  
- Chunking and embedding are crucial steps to handle large documents and capture their semantic meaning effectively.  
- Hybrid search leverages both exact phrase matching and vector similarity to improve search relevance, especially for natural language queries.  
- Integrating vision and other AI services enriches the searchable content beyond plain text.  
- This approach is foundational for advanced AI scenarios like retrieved augmented generation with generative AI models.
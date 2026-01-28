### 🎤 [00:03:12 – 00:08:24] Azure AI Search  
**Timestamp**: 00:03:12 – 00:08:24

**Key Concepts**  
- Azure AI Search provides an API endpoint to query indexes built over various data sources.  
- Indexes represent structured references to specific information sources (e.g., blobs, databases).  
- Supports both lexical (keyword-based) and semantic (meaning-based) search methods.  
- Semantic search uses vector embeddings to capture the meaning of data and queries.  
- Reciprocal rank fusion combines lexical and semantic search results for improved relevance.  
- Semantic re-ranking further refines results based on confidence scoring.  
- Searches are performed against a single index representing a single information source.  
- Azure AI Search forms the foundation of a Retrieval-Augmented Generation (RAG) 1.0 stack.

**Definitions**  
- **Index**: A structured representation of a particular set of information (e.g., a blob container or database) used to enable efficient search.  
- **Lexical Search**: Keyword-based search matching exact terms or phrases in the indexed data.  
- **Semantic Search**: Search based on the meaning of words and phrases, using vector embeddings to find conceptually similar information.  
- **Vector Embeddings**: High-dimensional numerical representations of text chunks that capture semantic meaning.  
- **Reciprocal Rank Fusion**: A method to combine rankings from multiple search approaches (lexical and semantic) to produce a unified, more relevant result list.  
- **Semantic Re-rank**: A post-processing step that reorders search results by comparing them again to the query to improve accuracy and confidence.

**Key Facts**  
- Azure AI Search creates indexes for each distinct data source.  
- Queries to Azure AI Search are sent via API calls targeting specific indexes.  
- The system chunks data into blocks to generate vector embeddings for semantic search.  
- Both lexical and vector-based searches run in parallel, then results are fused and re-ranked.  
- The final results returned meet a confidence threshold to ensure quality.  
- Current searches operate on a single index at a time, limiting the scope to one information source per query.

**Examples**  
- Searching by SKU or product name uses lexical keyword search due to high discrimination ability.  
- The idiom “it’s raining cats and dogs” illustrates the need for semantic understanding rather than literal keyword matching.

**Key Takeaways 🎯**  
- Azure AI Search enhances traditional keyword search by integrating semantic search capabilities.  
- Combining lexical and semantic search results yields higher quality and more relevant answers.  
- Vector embeddings are crucial for capturing the meaning behind natural language queries and data.  
- The approach supports Retrieval-Augmented Generation by enriching prompts with relevant, high-quality information from company data.  
- Each search is limited to a single index, representing one data source, forming the basis of a RAG 1.0 architecture.  
- Understanding the distinction between information (raw data) and knowledge (contextualized, meaningful data) is important when using Azure AI Search.
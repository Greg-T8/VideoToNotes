### 🎤 [00:18:49 – 00:22:31] Reasoning effort  
**Timestamp**: 00:18:49 – 00:22:31

**Key Concepts**  
- Reasoning effort levels control how the AI agent queries knowledge sources.  
- Agentic RAG (Retrieval-Augmented Generation) enables multi-hop reasoning and selective querying.  
- Different reasoning effort settings: minimal, low, medium, each affecting the agent’s behavior.  
- Knowledge source descriptions and retrieval instructions guide the agent’s planning and selection.  
- The agent can break down queries into sub-queries and selectively use knowledge sources based on complexity.  

**Definitions**  
- **Reasoning Effort**: The level of cognitive work the AI agent applies when deciding how to query knowledge sources, ranging from minimal (simple, broad querying) to medium (planned, selective querying).  
- **Agentic RAG**: A multi-hop retrieval-augmented generation approach where the agent intelligently plans and reasons about which knowledge sources to query and how to combine information.  

**Key Facts**  
- Minimal reasoning effort: The agent sends the original query to all knowledge sources without filtering or planning.  
- Low and medium reasoning effort: The agent analyzes knowledge source descriptions and retrieval instructions to plan queries efficiently.  
- Minimal effort mode may be disabled (grayed out) depending on the model or output mode used (e.g., web mode forces certain settings).  
- Quality and clarity of knowledge source descriptions are critical for effective reasoning and source selection.  

**Examples**  
- A knowledge source labeled "YouTube" with the description: "Transcripts from John Savill's technical training, YouTube channel content."  
- Another knowledge source described as "search of web information."  
- For simple questions, the agent may select a single knowledge source; for complex questions, it may query multiple sources with sub-queries.  

**Key Takeaways 🎯**  
- Reasoning effort settings directly influence how the AI agent interacts with knowledge sources—higher effort means smarter, more selective querying.  
- Providing detailed and accurate descriptions for each knowledge source helps the agent make better decisions during reasoning.  
- The agent’s ability to break down queries and selectively use sources improves efficiency and relevance of responses.  
- Understanding and configuring reasoning effort is essential for optimizing AI app performance when using multiple knowledge bases.  

---
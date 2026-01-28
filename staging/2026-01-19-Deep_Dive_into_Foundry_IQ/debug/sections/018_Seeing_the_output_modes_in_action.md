### 🎤 [00:28:31 – 00:33:11] Seeing the output modes in action  
**Timestamp**: 00:28:31 – 00:33:11

**Key Concepts**  
- Two main output modes when querying knowledge bases with generative AI:  
  1. **Extractive data mode** – returns raw chunks of relevant data/documents from the knowledge base.  
  2. **Answer synthesis mode** – generates a natural language answer synthesized from multiple knowledge sources.  
- Choice of output mode depends on the application’s needs (e.g., rich agent vs. simple chat app).  
- Debugging and inspecting returned data helps understand what the AI is doing behind the scenes.

**Definitions**  
- **Extractive data mode**: A mode where the AI returns a set of relevant documents or data chunks retrieved from the knowledge base without further processing or summarization.  
- **Answer synthesis mode**: A mode where the AI generates a coherent, natural language answer by synthesizing information from various knowledge sources, including indexes and the web.

**Key Facts**  
- In extractive mode, the system retrieved 11 documents as chunks from the knowledge base.  
- Answer synthesis mode can combine multiple sources such as an index and the web.  
- Answer synthesis typically takes longer to process than extractive mode.  
- The synthesized answer includes references to the sources used.  
- Different knowledge sources (e.g., BLOB, OneLake, web) influence the mode used; web sources require answer synthesis.  
- Medium reasoning effort can be configured for answer synthesis.

**Examples**  
- Asking “What is ExpressRoute?” in extractive mode returns raw document chunks from the knowledge base.  
- Asking the same question in answer synthesis mode returns a fully formed natural language answer along with source references.  
- A demonstration app uses three knowledge sources (BLOB, OneLake, web) and performs answer synthesis with medium reasoning effort.

**Key Takeaways 🎯**  
- Use extractive data mode when building rich agents that need raw data to reason over themselves.  
- Use answer synthesis mode for simpler chat applications that want a direct, natural language answer without additional processing.  
- Inspecting debug output is valuable to understand the AI’s behavior and the data it uses.  
- The choice of output mode should align with the intended user experience and application complexity.  
- Knowledge sources impact the mode: web-based sources necessitate answer synthesis.  
- Answer synthesis provides a more user-friendly, complete answer but requires more processing time.  

---
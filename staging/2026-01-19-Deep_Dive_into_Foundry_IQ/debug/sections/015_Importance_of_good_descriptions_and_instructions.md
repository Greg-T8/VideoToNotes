### 🎤 [00:22:31 – 00:23:51] Importance of good descriptions and instructions  
**Timestamp**: 00:22:31 – 00:23:51

**Key Concepts**  
- Quality descriptions of knowledge sources are crucial for effective selection by the model.  
- The model uses descriptions to decide which knowledge sources to query based on the question complexity.  
- Providing clear instructions guides the model on prioritizing knowledge sources during query planning.  
- Agentic multi-hop querying involves creating a chain of thought or query plan to select and execute queries across sources.  

**Definitions**  
- **Knowledge Source (KS)**: A repository or dataset (e.g., YouTube transcripts, web search) that the model can query for information.  
- **Agentic Multi-hop**: A process where the model plans multiple queries across different knowledge sources in a sequence to answer complex questions.  

**Key Facts**  
- Descriptions help the model understand the content and relevance of each knowledge source.  
- Instructions can specify priority, e.g., always use a technical YouTube knowledge source first for technical questions, then fallback to web search if needed.  
- The model’s decision-making involves a train of thought to select the most appropriate knowledge sources.  

**Examples**  
- YouTube knowledge source described as: "Transcripts from John Savill's technical training, YouTube channel content."  
- Instruction example: For technical items, prioritize the YouTube knowledge source first; if no answer found, then use the web search knowledge source.  

**Key Takeaways 🎯**  
- Always provide clear, quality descriptions for each knowledge source to enable accurate source selection by the model.  
- Use explicit instructions to guide the model’s query strategy and source prioritization.  
- Good descriptions and instructions improve the model’s ability to create an effective multi-hop query plan and solve complex problems efficiently.  
- This approach supports a self-reflective process where the model can reassess and refine its queries if initial attempts do not yield satisfactory answers.  

---
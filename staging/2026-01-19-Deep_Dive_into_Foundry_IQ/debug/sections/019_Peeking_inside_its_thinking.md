### 🎤 [00:33:11 – 00:34:37] Peeking inside its thinking  
**Timestamp**: 00:33:11 – 00:34:37

**Key Concepts**  
- Using different knowledge sources (BLOB, OneLake, web) to answer queries  
- Answer synthesis vs. extractive data retrieval based on use case  
- Visibility into the internal reasoning and processing steps of the AI system  
- Iterative planning and multiple retrieval calls in generating answers  
- Transparency in AI operations to understand how answers are formed  

**Definitions**  
- **Answer Synthesis**: The process where the AI generates a full, composed answer by integrating information from multiple sources, often involving reasoning and extrapolation.  
- **Extractive Data Option**: A retrieval mode where the AI returns only the most relevant data or information without generating a synthesized answer.  

**Key Facts**  
- The example system uses three knowledge sources: BLOB storage, OneLake, and the web  
- When using the web as a source, answer synthesis is required  
- The system performed 2 iterations (planning cycles)  
- It executed 11 different activities and 60 retrieval calls during the process  
- Detailed metrics available include elapsed time, planning tokens, query planning steps, and references used  

**Examples**  
- A demonstration from the product group showing the AI querying a knowledge base with multiple sources and revealing behind-the-scenes details of its reasoning process  
- The system’s output includes the number of iterations, activities, retrieval calls, and the step-by-step query planning and execution  

**Key Takeaways 🎯**  
- Foundry IQ enables querying a unified knowledge base that intelligently integrates multiple data sources  
- Users can choose between getting raw relevant data or a fully synthesized answer depending on their needs  
- The system provides transparency by exposing its internal reasoning steps, helping users understand how answers are derived  
- This visibility into the AI’s “thinking” process enhances trust and debugging capabilities for complex queries  
- The ultimate goal is to deliver high-quality inferencing and flexible answer generation for agents or applications using the knowledge base  

---
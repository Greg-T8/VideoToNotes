### 🎤 [00:25:39 – 00:28:31] Output modes  
**Timestamp**: 00:25:39 – 00:28:31

**Key Concepts**  
- Output modes determine how data is returned from knowledge base queries.  
- Two main output modes: **extractive data** and **answer synthesis**.  
- Answer synthesis is only available when using low and medium reasoning levels and requires the knowledge source to exclude web content.  
- Extractive data mode returns relevant data snippets for the generative model to reason over and produce answers.  
- Answer synthesis mode performs more advanced reasoning and synthesis of answers directly.  

**Definitions**  
- **Extractive data**: An output mode where the system returns relevant data excerpts from the knowledge base, leaving the generative model to reason and formulate the final answer.  
- **Answer synthesis**: An output mode where the system synthesizes and generates answers directly from the knowledge base content, involving more reasoning steps.  

**Key Facts**  
- When the knowledge source includes web content, only answer synthesis mode is allowed; minimal reasoning cannot be selected.  
- Answer synthesis mode is disabled (grayed out) if web is included as a knowledge source.  
- Extractive data mode is the default and compatible with all knowledge sources.  
- The API request changes from querying indexes to querying knowledge bases or knowledge sources when using these output modes.  

**Examples**  
- Using extractive data mode with a knowledge base to answer the question: "What is ExpressRoute?"  
- The system queries the knowledge base, retrieves relevant data, and then the generative model reasons over this data to produce the answer.  

**Key Takeaways 🎯**  
- Choose extractive data mode if you want raw relevant data returned for your own reasoning or processing.  
- Use answer synthesis mode for more advanced, integrated answer generation but only when web content is not part of the knowledge sources.  
- The choice of output mode affects API behavior and capabilities such as reasoning level and source selection.  
- Understanding output modes is crucial for configuring knowledge base queries effectively in Azure AI search scenarios.
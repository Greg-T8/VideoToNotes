### 🎤 [00:01:31 – 00:03:12] RAG to the rescue  
**Timestamp**: 00:01:31 – 00:03:12

**Key Concepts**  
- Pre-trained AI models have limitations because they only know data they were trained on.  
- To utilize information outside the model’s training data, additional relevant data must be provided at request time.  
- Retrieval-Augmented Generation (RAG) is the process of retrieving external information to augment the model’s response generation.  
- The quality and relevance of the retrieved data directly impact the quality of the AI model’s output.  
- Azure AI Search can be used to retrieve relevant data from various company data sources to feed into the model.

**Definitions**  
- **Retrieval-Augmented Generation (RAG)**: A method where additional information is retrieved from external sources and added to the prompt to enhance the AI model’s response capabilities.

**Key Facts**  
- AI models have cutoff dates and do not inherently know company-specific or updated data.  
- The application first queries the external data source, receives relevant information, then appends it to the prompt sent to the AI model.  
- Garbage in, garbage out principle applies: poor quality or irrelevant data leads to poor AI responses.  
- Azure AI Search exposes an API endpoint and creates indexes to facilitate retrieval of relevant data.

**Examples**  
- Using an internal company database or other knowledge bases as the external data source to retrieve relevant information before querying the AI model.  
- Azure AI Search acting as the retrieval mechanism to provide relevant data to augment the prompt.

**Key Takeaways 🎯**  
- AI models alone cannot answer questions about data they were not trained on; external data must be retrieved and provided.  
- RAG is a common and effective approach to enhance AI responses by combining model knowledge with up-to-date or proprietary information.  
- Ensuring the retrieved data is high quality and relevant is critical for obtaining useful AI outputs.  
- Tools like Azure AI Search simplify the retrieval process by indexing data and exposing APIs for integration with AI applications.
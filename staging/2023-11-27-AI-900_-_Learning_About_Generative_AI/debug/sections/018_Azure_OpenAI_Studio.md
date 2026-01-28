### 🎤 [00:45:44 – 00:48:41] Azure OpenAI Studio  
**Timestamp**: 00:45:44 – 00:48:41

**Key Concepts**  
- Azure OpenAI Studio is a portal to manage and interact with deployed OpenAI models on Azure.  
- Models available include GPT-4, GPT-3.5 turbo variants, embedding models (e.g., ADA2), and fine-tuned models.  
- Interaction with models can be done via endpoints and API keys provided in the Azure portal.  
- The Studio provides a playground interface for testing models with chat or completion formats depending on the model version.  
- System instructions (system messages) define the behavior or role of the model (e.g., marketing assistant).  
- Few-shot examples can be added to guide the model’s responses more precisely.  
- Various parameters can be tuned such as maximum response size (token limit), creativity, and randomness.  
- Grounding the model with external data sources (internet search, databases, HR systems) is important for domain-specific or updated knowledge.  
- Microsoft offers tools like the Semantic Kernel to orchestrate calls to the language model and integrate with other Azure services like Azure AI Search.

**Definitions**  
- **Azure OpenAI Studio**: A web interface within Azure that allows users to manage OpenAI model deployments, view keys/endpoints, and interact with models via a playground.  
- **System Instructions (System Message)**: Predefined prompts that set the context or role for the AI model to follow during interaction.  
- **Few-shot Examples**: Sample input-output pairs provided to the model to guide its behavior and improve response relevance.  
- **Semantic Kernel**: A Microsoft service that acts as an orchestrator to integrate large language models with other services and data sources.

**Key Facts**  
- Creating the Azure OpenAI service itself does not incur cost; charges are based on usage measured in tokens processed (prompt tokens and completion tokens).  
- Different models have varying context sizes and capabilities (e.g., GPT-4, GPT-3.5 turbo, ADA2 embedding).  
- Each deployment provides two API keys which can be regenerated if compromised.  
- The playground supports chat format for GPT models and completion format for earlier models.  
- Parameters like max tokens, creativity, and randomness can be adjusted in the playground.  
- Grounding the model with external data is recommended to avoid relying solely on the model’s pre-trained knowledge.

**Examples**  
- Using the playground to ask: “How would I make a cherry pie?” and receiving a response from a specific deployed GPT model.  
- Setting the system message to make the model act as a “marketing writing assistant.”  
- Demonstrating that the model does not know who “John Savile” is without grounding or additional data.  

**Key Takeaways 🎯**  
- Azure OpenAI Studio is a powerful tool for managing and experimenting with OpenAI models deployed on Azure.  
- Customizing system instructions and few-shot examples allows tailoring the AI’s behavior to specific tasks.  
- Tuning parameters like token limits and creativity helps control the output quality and style.  
- Grounding AI responses with external, domain-specific data is crucial for accuracy and relevance in real-world applications.  
- Microsoft’s Semantic Kernel and Azure AI Search can be leveraged to integrate AI models with broader data and services, enhancing their usefulness.
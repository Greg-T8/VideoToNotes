### 🎤 [00:11:55 – 00:14:22] Remote knowledge sources  
**Timestamp**: 00:11:55 – 00:14:22

**Key Concepts**  
- Remote knowledge sources allow AI applications to access information beyond local indexes.  
- Integration with Microsoft 365 (M365) semantic index enables retrieval of relevant data based on user tokens.  
- Use of external web search powered by Bing as a remote knowledge source.  
- MCP (Microsoft Connected Platform) as a standard protocol to provide additional knowledge, tools, and prompts to AI applications.  
- Reflection of capabilities by MCP allows AI apps to understand how to use the knowledge source without manual explanation.  
- Azure AI Search can index data from sources like SharePoint sites or OneLake, respecting permissions.  
- Different knowledge sources can be combined into knowledge bases within Azure AI Search.  

**Definitions**  
- **Remote knowledge sources**: External or non-local data repositories or services that an AI application can query to retrieve relevant information.  
- **M365 semantic index**: A Microsoft 365 service that indexes content semantically to enable relevant search results personalized by user context.  
- **MCP (Microsoft Connected Platform)**: A standard protocol that exposes knowledge and tools (including search capabilities) to AI applications, allowing them to dynamically understand and use these resources.  

**Key Facts**  
- Access to M365 semantic index requires a Copilot license.  
- Web search is powered by Bing and can be used as a remote knowledge source.  
- MCP is currently in preview and supports exposing search tools as part of its capabilities.  
- Azure AI Search creates indexes for data from sources like SharePoint or OneLake while retaining permissions.  
- Using SharePoint in general (not a specific site) defaults to using M365 Work IQ semantic index.  
- AI apps and users experience no difference whether data is local or from remote knowledge sources.  

**Examples**  
- Specific SharePoint site as a knowledge source.  
- General M365 Work IQ / SharePoint semantic index usage.  
- Web search via Bing as a remote knowledge source.  
- MCP providing additional knowledge and tools, including search capabilities.  
- In Microsoft Foundry, a user selects an Azure AI Search resource and creates knowledge bases composed of multiple knowledge sources (e.g., Azure AI Search Index and web).  

**Key Takeaways 🎯**  
- Remote knowledge sources expand AI app capabilities by integrating diverse data repositories seamlessly.  
- Licensing (Copilot) and protocols (MCP) are important considerations for accessing certain semantic indexes and tools.  
- Azure AI Search manages indexing and permissions, ensuring secure and relevant data retrieval.  
- MCP standardizes how AI apps discover and use external knowledge sources, reducing manual configuration.  
- Combining multiple knowledge sources into knowledge bases allows flexible and powerful AI-driven search experiences.
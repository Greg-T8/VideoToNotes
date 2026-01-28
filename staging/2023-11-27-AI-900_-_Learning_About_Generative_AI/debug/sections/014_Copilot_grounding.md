### 🎤 [00:37:04 – 00:39:56] Copilot grounding  
**Timestamp**: 00:37:04 – 00:39:56

**Key Concepts**  
- Copilots operate within the context of specific applications (e.g., Teams, Word, security dashboards, Dynamics, Bing).  
- Copilot orchestration involves interpreting user requests and performing "grounding" by fetching relevant external data.  
- Grounding means retrieving additional data from APIs or other sources to enrich the prompt before sending it to the large language model (LLM).  
- Different copilots use different data sources depending on their domain (e.g., Microsoft Graph for Microsoft 365, Bing search index for Bing, Sentinel data for security copilots).  
- The copilot creates a meta prompt combining user input and grounded data to enable the LLM to generate accurate and useful responses.  
- Copilots may instruct the LLM to invoke APIs or commands on their behalf, leveraging permissions granted by the user.  
- The LLM itself has no direct access to user data or external systems; all data access and command execution are mediated by the copilot.  
- Copilots help users by accelerating tasks, providing guidance when users are unsure, and acting as a generative AI service integrated into applications.

**Definitions**  
- **Grounding**: The process of retrieving and appending relevant external data (via APIs or other sources) to a user’s prompt so that the large language model can generate a more accurate and contextually relevant response.  
- **Copilot orchestration**: The mechanism by which a copilot interprets user requests, determines necessary external data, performs grounding, and constructs the final prompt for the large language model.

**Key Facts**  
- Microsoft 365 copilots use Microsoft Graph API for grounding data.  
- Bing copilot grounds itself using the Bing internet search index.  
- Security copilots use Microsoft Graph and Sentinel data, among other APIs.  
- The copilot has permissions to run commands on behalf of the user as instructed by the LLM.  
- The LLM itself has no direct data access or permissions; it relies entirely on the copilot for data and actions.

**Examples**  
- Summarizing emails from a manager by fetching those emails first and appending them to the prompt.  
- Summarizing the last meeting by retrieving the meeting transcript and including it in the prompt.  
- A security copilot accessing Sentinel data and Microsoft Graph to respond to queries.  
- Bing copilot performing internet searches to ground answers in up-to-date web content.

**Key Takeaways 🎯**  
- Copilots enhance LLM capabilities by grounding prompts with real, relevant data from appropriate sources.  
- Grounding is essential because LLMs do not have inherent access to user data or external systems.  
- Copilots act as intermediaries that manage data retrieval, permissions, and command execution securely on behalf of users.  
- This architecture enables copilots to provide accurate, context-aware assistance across diverse applications without exposing sensitive data directly to the LLM.  
- Thinking of copilots as generative AI SaaS solutions helps understand their role as complete services that perform tasks autonomously for users.
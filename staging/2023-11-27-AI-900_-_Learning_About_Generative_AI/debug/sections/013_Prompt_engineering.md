### 🎤 [00:35:06 – 00:37:04] Prompt engineering  
**Timestamp**: 00:35:06 – 00:37:04

**Key Concepts**  
- Quality of the prompt directly impacts the quality of the response from a large language model (LLM).  
- Being explicit and exact in prompts is crucial.  
- Prompt engineering involves designing prompts to improve task outcomes.  
- Different prompting techniques:  
  - **Zero shot**: No examples given, just the instruction.  
  - **Few shot**: Providing examples of user input and desired agent responses.  
- Grounding: Incorporating external data sources into the prompt to provide context the LLM does not inherently have.  

**Definitions**  
- **Prompt engineering**: The science and practice of crafting prompts to improve the effectiveness and accuracy of responses from language models.  
- **Zero shot**: A prompting method where the model is given a task without any example inputs or outputs.  
- **Few shot**: A prompting method where the model is given a few examples of inputs and desired outputs to guide its response.  
- **Grounding**: The process of appending relevant external data (e.g., emails, meeting transcripts) to a prompt so the LLM can use that information to perform the task.  

**Key Facts**  
- Large language models do not have access to personal or external data by default. Grounding is necessary to provide that context.  
- Grounding enables tasks like summarizing emails or meeting transcripts by fetching and appending that data to the prompt.  

**Examples**  
- Summarize all emails from a manager by grounding the prompt with those emails.  
- Summarize the last meeting by grounding the prompt with the meeting transcript.  

**Key Takeaways 🎯**  
- The effectiveness of AI responses depends heavily on how well prompts are engineered.  
- Explicit and exact instructions improve model performance.  
- Using zero shot and few shot techniques can guide the model’s behavior.  
- Grounding is essential to incorporate real-world data that the model cannot access on its own.  
- Co-pilots in applications use prompt engineering and grounding to tailor responses within specific contexts (e.g., Teams, Word, security dashboards).
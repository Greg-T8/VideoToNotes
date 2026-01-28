### 🎤 [00:23:51 – 00:25:39] Self-reflection  
**Timestamp**: 00:23:51 – 00:25:39

**Key Concepts**  
- Multi-hop query planning and execution for problem solving  
- Self-reflection step to evaluate if the query results have sufficiently answered the question  
- Different effort levels (minimal, low, medium) affect query planning, source selection, and self-reflection  
- Higher effort levels enable additional retrieval passes and richer response classification  

**Definitions**  
- **Self-reflection**: A process where, after executing a query plan and retrieving results, the system reviews the results against the original goal to determine if the problem is solved. If not, it can perform a follow-up query to improve the answer.  
- **Effort levels**: Settings that control the depth of query planning and reasoning:  
  - *Minimal*: No source selection or planning; searches all sources simply and quickly.  
  - *Low/Medium*: Includes source selection, query planning, and self-reflection with additional retrieval and classification steps.  

**Key Facts**  
- Medium effort includes a self-reflection step that can trigger a second retrieval pass if the initial results are insufficient.  
- Higher effort levels consume more tokens, increase latency, and cost more but yield higher quality responses.  
- Minimal effort skips source selection and planning, does not use web as a knowledge source grounding.  
- Low and medium efforts perform source selection, query planning, and self-reflection.  
- Reflective retrieval and classification add richer capabilities to responses at low and medium levels.  

**Examples**  
- None explicitly mentioned beyond the description of how minimal vs. medium effort modes operate.  

**Key Takeaways 🎯**  
- Choosing the effort level balances cost, speed, and answer quality.  
- Self-reflection enables iterative improvement of answers by reassessing query results and performing follow-ups if needed.  
- Minimal effort is fast and basic but less precise; medium effort is more thorough with additional reasoning and retrieval steps.  
- Source selection and query planning are critical for higher quality responses and are enabled starting at low effort level.  
- Understanding these modes helps optimize the use of knowledge sources and response quality in AI agents.  

---
### 🎤 [03:54:57 – 03:59:05] Log Analytics Workspace  
**Timestamp**: 03:54:57 – 03:59:05

**Key Concepts**  
- Different types of Log Analytics workspaces exist with varying capabilities and costs.  
- Data ingestion, storage, and query execution all contribute to costs.  
- Retention policies affect whether data is stored interactively or moved to archive.  
- Archive storage allows long-term retention but limits direct querying without restore/search jobs.  
- Basic logs offer a cost-effective but limited subset of KQL and shorter retention.  
- Analytics logs provide full KQL capabilities and longer retention periods.  
- Tables within a workspace can be configured to use either analytics or basic logs.  
- Network Watcher integrates with Log Analytics for network health and troubleshooting.

**Definitions**  
- **Log Analytics Workspace**: A centralized repository for collecting, storing, and analyzing log data using Kusto Query Language (KQL).  
- **Analytics Logs**: Full-featured logs with complete KQL support, longer retention (30-90 days interactive), and higher cost.  
- **Basic Logs**: Logs with a subset of KQL capabilities, cheaper, limited to 8 days of interactive retention, with additional costs for queries and storage.  
- **Archive Storage**: Long-term storage (up to 12 years) for logs beyond interactive retention; data is not directly queryable without restore or search jobs.  
- **KQL (Kusto Query Language)**: Query language used to analyze log data in Log Analytics.  
- **Network Watcher**: Azure service providing network monitoring and troubleshooting capabilities, integrated with Log Analytics.

**Key Facts**  
- Analytics logs retention: typically 30 days interactive, extendable to 90 days with Sentinel, and up to 2 years interactive in some cases.  
- Basic logs retention: 8 days interactive only; after that, data moves to archive.  
- Archive retention: up to 12 years, with storage costs and additional fees for restore/search jobs.  
- Costs include data ingestion, storage beyond included retention, and query execution (especially for basic logs and archive restores).  
- Basic logs do not support cross-table queries but can use consolidated schemas (e.g., container insights V2 schema) to mitigate this.  
- Changing table settings from analytics to basic affects how much data is interactive vs archived based on retention settings.  
- Example: Setting a 30-day retention with basic logs results in 8 days interactive and 22 days archived.

**Examples**  
- Container insights V2 schema allows storing all data in a single table, enabling use of basic logs despite KQL limitations.  
- Adjusting table retention from analytics to basic changes the split between interactive and archive data (e.g., 30 days total retention with basic logs results in 8 days interactive + 22 days archive).  
- Using Network Watcher for network health monitoring and troubleshooting integrated with Log Analytics.

**Key Takeaways 🎯**  
- Choose between analytics and basic logs based on cost, retention needs, and query capabilities.  
- Archive storage is cost-effective for long-term retention but requires paid restore/search jobs for querying.  
- Basic logs reduce costs but limit query complexity and retention duration.  
- Retention settings directly impact how much data remains interactive vs archived.  
- Use consolidated schemas like container insights V2 to optimize basic log usage.  
- Network Watcher complements Log Analytics by providing network-specific insights and troubleshooting tools.
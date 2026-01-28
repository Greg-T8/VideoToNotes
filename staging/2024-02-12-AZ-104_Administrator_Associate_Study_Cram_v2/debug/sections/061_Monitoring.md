### 🎤 [03:45:25 – 03:50:48] Monitoring  
**Timestamp**: 03:45:25 – 03:50:48

**Key Concepts**  
- Monitoring provides observability to ensure system health and performance.  
- Monitoring occurs at multiple layers: subscription level (control plane) and resource level.  
- Activity Log captures control plane changes at the subscription level.  
- Resources emit metrics (time-based signals) and logs, which need to be configured.  
- Diagnostic settings enable collection and routing of logs and metrics.  
- Logs and metrics can be sent to different destinations: Azure Storage, Event Hub, Log Analytics workspace.  
- Log Analytics workspace enables powerful analytics using Kusto Query Language (KQL).  
- Guest OS monitoring is possible via Azure Monitor agent and guest metrics.  
- Alerts can be created based on activity logs, metrics, or log queries to proactively notify issues.

**Definitions**  
- **Activity Log**: A free log that records control plane changes at the subscription level.  
- **Diagnostic Settings**: Configuration that enables collection of logs and metrics from resources and defines where to send them.  
- **Azure Monitor Metrics**: Time-based signals from resources that are free and provide workload-specific metrics.  
- **Log Analytics Workspace**: A centralized service for storing and analyzing logs with advanced querying capabilities using KQL.  
- **Event Hub**: A publish-subscribe service that can receive diagnostic data for external SIEM or processing.  
- **Guest Metrics**: Metrics collected from within the guest OS of a VM using Azure Monitor agent.  
- **Alerts**: Configurable notifications triggered by conditions on activity logs, metrics, or log queries.

**Key Facts**  
- Activity Log is free and scoped at subscription, resource group, or resource level.  
- Metrics are free and provide aggregated data (e.g., average CPU usage).  
- Logs do not exist by default and require diagnostic settings to be enabled.  
- Diagnostic data can be sent to multiple destinations simultaneously.  
- Azure Storage is the cheapest option for storing logs but less interactive.  
- Log Analytics workspace supports advanced analytics and querying with KQL.  
- VMs can provide detailed performance counters and logs when diagnostic settings are enabled.  
- Cosmos DB and other resources allow granular selection of diagnostic categories and destinations.  
- Alerts can be based on activity logs, metrics, or custom KQL queries and integrate with Azure Sentinel.

**Examples**  
- Viewing VM metrics such as availability, CPU, disk bytes, and CPU credits for B-series VMs.  
- Splitting metrics by LUN to get detailed disk usage insights.  
- Configuring diagnostic settings on Cosmos DB to capture specific logs and metrics and send them to chosen destinations.  
- Using App Insights for application-level monitoring and synthetic transaction tests.  

**Key Takeaways 🎯**  
- Monitoring is essential for maintaining system health and requires observability at multiple layers.  
- Always enable diagnostic settings to collect logs and metrics beyond default metrics.  
- Choose appropriate destinations for diagnostic data based on cost, usability, and integration needs.  
- Use Log Analytics workspace for powerful querying and insights with KQL.  
- Implement alerts to proactively detect and respond to issues based on various data sources.  
- Extend monitoring to guest OS and application layers for comprehensive coverage.
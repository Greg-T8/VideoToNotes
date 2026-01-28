# Azure Update - 23rd January 2026 - Exam Notes

**Video:** [https://www.youtube.com/watch?v=FfYk17LiOmM](https://www.youtube.com/watch?v=FfYk17LiOmM)
**Published:** 2026-01-23

*Generated on 2026-01-27 13:07*

---

## Table of Contents

- [Introduction](#introduction)
- [New videos](#new-videos)
- [AKS deployment safeguards](#aks-deployment-safeguards)
- [StandardV2 NAT Gateway](#standardv2-nat-gateway)
- [User delegated SAS for more services](#user-delegated-sas-for-more-services)
- [AFS in Israel Central](#afs-in-israel-central)
- [ANF app volume group for Oracle data protection](#anf-app-volume-group-for-oracle-data-protection)
- [Azure Load Testing new region](#azure-load-testing-new-region)
- [App Testing reporting](#app-testing-reporting)
- [GitHub Copilot SDK](#github-copilot-sdk)
- [Close](#close)

## Introduction

**Timestamp**: 00:00:00 – 00:00:08

**Key Concepts**  
- None mentioned in the provided transcript segment

**Definitions**  
- None mentioned

**Key Facts**  
- None mentioned

**Examples**  
- None mentioned

**Key Takeaways 🎯**  
- No content available for this time range to extract notes from

---

## New videos

**Timestamp**: 00:00:08 – 00:00:48

**Key Concepts**  
- Release of only one new video this week  
- The video covers the security part of a keynote presentation  
- Mention of Fabric IQ and Work IQ in relation to the video content  
- Encouragement to attend AI tours at various locations  

**Definitions**  
- **Fabric IQ and Work IQ**: (No explicit definitions provided in this segment)  

**Key Facts**  
- Only one video released this week due to the speaker being in New York  
- The video focuses on security aspects presented in a keynote  

**Examples**  
- The speaker participated in the security portion of a keynote in New York  
- AI tours are available in multiple locations (encouraged to attend)  

**Key Takeaways 🎯**  
- This week’s video content is limited but focused on security in a keynote context  
- Fabric IQ and Work IQ are related topics but not elaborated here  
- Attending AI tours can provide additional insights and experiences related to the content  

---

## AKS deployment safeguards

**Timestamp**: 00:00:48 – 00:01:36

**Key Concepts**  
- AKS (Azure Kubernetes Service) deployment safeguards are now generally available (GA).  
- Introduction of new pod security standards as part of deployment safeguards.  
- Centralized management of multiple security profiles: baseline, restricted, and privileged.  
- Security standards cover namespaces, privileged containers, exposed capabilities, mount types, volume usage, and route usage.  
- Deployment safeguards can be enabled on both new and existing AKS clusters.  
- Ability to exclude specific namespaces from these security policies if needed.

**Definitions**  
- **Deployment safeguards**: A set of controls and policies in AKS to enforce security standards during deployment.  
- **Pod security standards**: Predefined security profiles that govern pod configurations to enhance cluster security.  

**Key Facts**  
- Deployment safeguards and pod security standards are now GA in AKS.  
- Profiles include baseline, restricted, and privileged standards.  
- Covers a wide range of configurations including namespaces, container privileges, capabilities, mounts, volumes, and routes.  
- Supports application on existing clusters and allows namespace exclusions.

**Examples**  
- None mentioned explicitly.

**Key Takeaways 🎯**  
- AKS deployment safeguards provide a centralized and standardized way to enforce pod security policies.  
- Multiple security profiles allow flexibility depending on workload requirements.  
- The feature is flexible enough to be applied to existing clusters and allows exceptions for special namespaces.  
- This enhances security posture by controlling critical pod and container configurations at deployment time.

---

## StandardV2 NAT Gateway

**Timestamp**: 00:01:36 – 00:03:06

**Key Concepts**  
- NAT Gateway provides managed outbound internet access for resources within a virtual network.  
- StandardV2 NAT Gateway is the latest version, now generally available (GA).  
- Supports zone-redundant deployment, improving architecture flexibility and reliability.  
- Offers high throughput and packet processing capabilities.  
- Supports dual stack (IPv4 and IPv6) with multiple IP addresses for outbound traffic.  
- Enables flow logs for traffic monitoring and insights.

**Definitions**  
- **NAT Gateway**: A managed service that allows resources inside a virtual network to access the internet outbound while hiding their private IPs behind public IP addresses.  
- **Zone-redundant**: A deployment that spans multiple availability zones to increase availability and fault tolerance.  
- **Dual stack support**: Ability to handle both IPv4 and IPv6 addresses simultaneously.  
- **Flow logs**: Logs that capture information about IP traffic flowing through the NAT Gateway for monitoring and diagnostics.

**Key Facts**  
- StandardV2 NAT Gateway supports zone-redundant configurations, unlike the previous version which was regional or zonal only.  
- Throughput capacity: up to 100 gigabits per second.  
- Packet processing capacity: up to 10 million packets per second.  
- Can attach up to 16 IPv4 and IPv6 addresses for outbound traffic source IPs.  
- Flow logs can be enabled for detailed traffic insights.

**Examples**  
- None mentioned explicitly, but the explanation implies use in architectures requiring zone redundancy and high throughput for outbound internet access.

**Key Takeaways 🎯**  
- StandardV2 NAT Gateway significantly enhances network architecture by supporting zone redundancy, removing the need to align NAT gateways with specific subnets or zones.  
- High throughput and packet capacity make it suitable for demanding workloads.  
- Dual stack and multiple IP address support allow flexible outbound IP management and security controls.  
- Enabling flow logs provides valuable visibility into outbound traffic patterns.

---

## User delegated SAS for more services

**Timestamp**: 00:03:06 – 00:04:01

**Key Concepts**  
- User-delegated Shared Access Signatures (SAS) are now available for Azure Tables, Files, and Queues, extending beyond the previously supported Blob service.  
- User-delegated SAS provides a more secure alternative to account or service SAS tokens.  
- The SAS token is signed by the delegated identity (an Azure Active Directory account) rather than the storage account keys.  
- Permissions granted by user-delegated SAS cannot exceed those of the identity creating the delegation.  
- User-delegated SAS tokens have a maximum validity period of seven days.

**Definitions**  
- **User-delegated SAS**: A type of Shared Access Signature signed by an Azure AD identity rather than storage account keys, offering more granular and secure access control.  
- **Account or Service SAS**: SAS tokens signed by storage account keys, which have broad and powerful permissions.

**Key Facts**  
- User-delegated SAS is now supported for Tables, Files, and Queues (previously only for Blobs).  
- User-delegated SAS tokens can only be valid for up to 7 days.  
- Permissions of the SAS token are limited to or less than the permissions of the Azure AD identity that creates it.

**Examples**  
- None mentioned explicitly in this segment.

**Key Takeaways 🎯**  
- User-delegated SAS enhances security by leveraging Azure AD identities instead of storage account keys.  
- It limits the scope and lifetime of access tokens, reducing risk from over-permissioned or long-lived SAS tokens.  
- This feature now applies to more Azure Storage services, enabling consistent secure access patterns across Blobs, Tables, Files, and Queues.

---

## AFS in Israel Central

**Timestamp**: 00:04:01 – 00:04:52

**Key Concepts**  
- Azure File Sync (AFS) enables synchronization of Windows File Server SMB shares via Azure File Shares in the cloud.  
- AFS allows local SMB shares to offload content to the cloud when running out of local capacity, maintaining the appearance of files locally.  
- When offloaded files are accessed, they are pulled back down from the cloud, which may introduce latency.  
- Sync services deployed in multiple locations reduce latency and help meet data residency requirements.

**Definitions**  
- **Azure File Sync (AFS)**: A service that synchronizes Windows File Server SMB shares with Azure File Shares, enabling cloud-based storage and seamless local access.  
- **SMB Share**: A network file share protocol used by Windows File Servers to share files over a network.  
- **Azure File Share**: Cloud-based file storage accessible via SMB protocol, used as the backend for Azure File Sync.

**Key Facts**  
- Azure File Sync is now available in the Israel Central region.  
- Offloaded files are not stored locally but still appear available to users.  
- Accessing offloaded files causes them to be downloaded from the cloud, resulting in increased latency.  
- Deploying sync services in different geographic locations reduces lag and supports compliance with data residency requirements.

**Examples**  
- If a Windows File Server SMB share runs out of capacity, Azure File Sync can offload content to the Azure File Share, freeing local space while keeping files accessible.  
- When a user tries to open an offloaded file, it is retrieved from the cloud, causing some delay but maintaining seamless access.

**Key Takeaways 🎯**  
- Azure File Sync extends local file server capacity by leveraging cloud storage transparently.  
- Offloading files helps manage local storage limits without disrupting user access.  
- Deploying sync services regionally improves performance and compliance.  
- Availability of AFS in Israel Central expands options for customers in that region.

---

## ANF app volume group for Oracle data protection

**Timestamp**: 00:04:52 – 00:05:47

**Key Concepts**  
- Azure NetApp Files (ANF) app volume groups for Oracle now support data protection volumes.  
- Oracle databases typically use multiple volumes (2 to 12) depending on size and configuration.  
- App volume groups automate creation of all necessary volumes following best practices.  
- Support for cross-zone and cross-region replication is available.  
- Replication sends only changed blocks to optimize data transfer.  
- Data protection features currently enabled via REST API.  
- Goal: safeguard Oracle database data against threats and disruptions, ensuring continuous availability.

**Definitions**  
- **App volume group for Oracle**: A collection of multiple volumes configured together to support an Oracle database environment, adhering to best practices for volume setup.  
- **Data protection volume support**: Capability to replicate and protect volumes containing Oracle data to prevent data loss and ensure availability.  
- **Cross-zone and cross-region replication**: Replication methods that allow data to be copied across different availability zones or geographic regions for resilience.

**Key Facts**  
- Oracle databases typically require between 2 and 12 volumes.  
- Replication transmits only changed data blocks, improving efficiency.  
- Data protection replication is currently enabled through REST API calls.

**Examples**  
- None mentioned explicitly.

**Key Takeaways 🎯**  
- Using ANF app volume groups simplifies managing multiple Oracle database volumes.  
- Data protection via replication helps maintain database availability and resilience.  
- Cross-zone and cross-region replication options provide flexibility for disaster recovery and compliance.  
- Although currently enabled via REST API, this feature is aimed at helping customers safeguard their Oracle data continuously.

---

## Azure Load Testing new region

**Timestamp**: 00:05:47 – 00:06:22

**Key Concepts**  
- Azure Load Testing is now available in a new region: Switzerland North.  
- It is a managed cloud service designed for high-scale load testing.  
- Supports multiple testing approaches: Apache JMeter, local scripts, and a web experience that generates scripts automatically.  
- Provides detailed analytics on component behavior under stress to help identify bottlenecks.

**Definitions**  
- **Azure Load Testing**: A managed cloud service that enables users to perform scalable load testing using cloud resources, supporting various scripting methods and providing analytics for performance insights.

**Key Facts**  
- New region added: Switzerland North.  
- Load testing can be performed using Apache JMeter, local scripts, or a web-based script generation tool.  
- Analytics include stress test results and component behavior insights.

**Examples**  
- Using Apache JMeter scripts or local scripts to simulate load.  
- Using the web experience to automatically generate load testing scripts.

**Key Takeaways 🎯**  
- Azure Load Testing’s expansion to Switzerland North enhances regional availability and performance.  
- Multiple flexible options for creating load tests make it accessible for different user preferences and scenarios.  
- Analytics provided by the service are crucial for identifying performance bottlenecks and optimizing applications under load.

---

## App Testing reporting

**Timestamp**: 00:06:22 – 00:07:08

**Key Concepts**  
- Azure App Testing now includes enhanced reporting features in General Availability (GA).  
- App Testing covers both load testing and end-to-end flow testing.  
- Integration of Playwright Workspaces reporting for cloud-scale web testing.  
- Enhanced debugging through storage account integration and trace viewer in the portal for deeper analysis.

**Definitions**  
- **Azure App Testing**: A service that supports load testing and end-to-end testing of applications, now with improved reporting capabilities.  
- **Playwright Workspaces reporting**: Reporting feature integrated into App Testing for detailed cloud-scale web testing insights.  
- **Trace viewer**: A tool accessible via the Azure portal that allows detailed examination of debugging data stored in a specified storage account.

**Key Facts**  
- Reporting update for App Testing is now generally available (GA).  
- Debugging requires specifying a storage account to store data for analysis.  
- The portal provides a trace viewer to interact with and analyze the stored debugging data.

**Examples**  
- Using the trace viewer through the Azure portal to perform deeper analysis of debugging data after enabling debugging and specifying a storage account.

**Key Takeaways 🎯**  
- Azure App Testing’s new reporting features simplify and speed up debugging and analysis of application tests.  
- Storing debugging data in a storage account enables detailed post-test analysis via the portal’s trace viewer.  
- Playwright Workspaces reporting enhances cloud-scale web testing capabilities within App Testing.

---

## GitHub Copilot SDK

**Timestamp**: 00:07:08 – 00:07:41

**Key Concepts**  
- GitHub Copilot now offers an SDK (Software Development Kit).  
- The SDK allows integration of GitHub Copilot capabilities into custom applications and experiences.  
- Advanced features of GitHub Copilot remain available through the SDK, including multi-step planning, use of multiple models, leveraging MCP servers, and building custom agents.  
- The SDK enables triggering GitHub Copilot functionality programmatically, beyond traditional CLI or VS Code integration.

**Definitions**  
- **GitHub Copilot SDK**: A software development kit that allows developers to embed GitHub Copilot’s AI-powered coding assistance into their own apps and workflows.

**Key Facts**  
- The SDK provides access to the same advanced capabilities as the GitHub Copilot CLI and VS Code integration.  
- Features supported include multi-step planning, multiple AI models, MCP servers, and custom agent creation.

**Examples**  
- Using GitHub Copilot SDK within custom applications or experiences instead of only through CLI or VS Code.

**Key Takeaways 🎯**  
- The GitHub Copilot SDK expands the ways developers can use Copilot by enabling integration into any app or workflow.  
- Developers retain access to all advanced Copilot features when using the SDK.  
- This flexibility allows for more tailored and powerful AI-assisted development experiences.

---

## Close

**Timestamp**: 00:07:41 – unknown

**Key Concepts**  
- Conclusion and wrap-up of the presentation or video.

**Definitions**  
- None mentioned.

**Key Facts**  
- None mentioned.

**Examples**  
- None mentioned.

**Key Takeaways 🎯**  
- The session has ended.  
- A polite sign-off wishing the audience well until the next video.

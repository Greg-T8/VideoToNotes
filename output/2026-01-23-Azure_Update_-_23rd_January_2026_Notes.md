# Azure Update - 23rd January 2026 - Exam Notes

**Video:** [https://www.youtube.com/watch?v=FfYk17LiOmM](https://www.youtube.com/watch?v=FfYk17LiOmM)
**Published:** 2026-01-23

*Generated on 2026-01-27 13:09*

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
- None explicitly mentioned in the provided transcript segment

**Definitions**  
- None provided

**Key Facts**  
- None provided

**Examples**  
- None mentioned

**Key Takeaways 🎯**  
- No specific information available from the transcript segment for this section

---

## New videos

**Timestamp**: 00:00:08 – 00:00:48

**Key Concepts**  
- Video content update: only one new video released this week  
- Presenter was in New York and contributed to the security part of a keynote  
- Mention of Fabric IQ and Work IQ in relation to the video content  

**Definitions**  
- None explicitly defined in this segment  

**Key Facts**  
- Only one video released this week due to travel commitments  
- The video covered the security portion of a keynote presentation  

**Examples**  
- Presenter’s participation in a keynote security segment in New York  

**Key Takeaways 🎯**  
- Video releases may be limited due to presenter availability  
- Security topics are a focus in recent video content  
- Fabric IQ and Work IQ are related topics, though details are not expanded here  
- Encouragement to attend AI tours locally (briefly mentioned)

---

## AKS deployment safeguards

**Timestamp**: 00:00:48 – 00:01:36

**Key Concepts**  
- AKS (Azure Kubernetes Service) deployment safeguards are now generally available (GA).  
- Introduction of new pod security standards as part of deployment safeguards.  
- Centralized management of different security profiles: baseline, restricted, and privileged.  
- Security standards cover multiple aspects including namespaces, privileged containers, exposed capabilities, mount types, volume usage, and routes.  
- Deployment safeguards can be enabled on both new and existing AKS clusters.  
- Ability to exclude specific namespaces from these security standards if needed.

**Definitions**  
- **Deployment safeguards**: A set of controls and standards in AKS to enhance security by managing pod security profiles and configurations centrally.  
- **Pod security standards**: Security profiles that define restrictions and permissions for pods, categorized as baseline, restricted, and privileged.

**Key Facts**  
- Deployment safeguards and pod security standards are now GA in AKS.  
- These standards apply across all namespaces and cover various security configurations.  
- Supports enabling on existing clusters, not just new deployments.  
- Namespace exclusions are supported for special cases.

**Examples**  
- None mentioned.

**Key Takeaways 🎯**  
- AKS deployment safeguards provide a centralized way to enforce pod security policies across clusters.  
- The new pod security standards help control critical security aspects such as container privileges and resource mounts.  
- Flexibility is provided by allowing exclusions of certain namespaces and applying safeguards to existing clusters.  
- This feature enhances security posture for Kubernetes workloads running on AKS.

---

## StandardV2 NAT Gateway

**Timestamp**: 00:01:36 – 00:03:06

**Key Concepts**  
- NAT Gateway provides managed outbound internet access for resources inside a virtual network.  
- StandardV2 NAT Gateway is the latest version, now generally available (GA).  
- Supports zone-redundant deployment, improving architecture flexibility and reliability.  
- Offers high throughput and packet processing capacity.  
- Supports dual stack IP addressing (IPv4 and IPv6).  
- Enables flow logs for traffic monitoring and insights.

**Definitions**  
- **NAT Gateway**: A managed service that allows resources within a virtual network to have outbound internet connectivity without exposing them directly.  
- **Zone-redundant**: A deployment model that spans multiple availability zones to increase availability and fault tolerance.  
- **Dual stack support**: The ability to handle both IPv4 and IPv6 addresses simultaneously.  
- **Flow logs**: Logs that capture information about IP traffic flowing through the NAT Gateway for monitoring and analysis.

**Key Facts**  
- StandardV2 NAT Gateway supports zone-redundant configurations, unlike the previous version which was regional or zonal only.  
- Throughput capacity: up to 100 gigabits per second.  
- Packet processing capacity: up to 10 million packets per second.  
- Can attach up to 16 IPv4 and IPv6 addresses for outbound traffic source IPs.  
- Flow logs can be enabled to gain detailed traffic insights.

**Examples**  
- None mentioned explicitly, but the explanation implies use in architectures requiring zone redundancy and high throughput for outbound internet access.

**Key Takeaways 🎯**  
- StandardV2 NAT Gateway significantly enhances network architecture flexibility by supporting zone redundancy.  
- It provides very high throughput and packet processing capabilities suitable for demanding workloads.  
- Dual stack support allows seamless handling of both IPv4 and IPv6 outbound traffic.  
- Enabling flow logs is recommended for better traffic visibility and security monitoring.  
- This upgrade removes previous limitations related to subnet and zone alignment in NAT Gateway deployments.

---

## User delegated SAS for more services

**Timestamp**: 00:03:06 – 00:04:01

**Key Concepts**  
- User-delegated Shared Access Signatures (SAS) are now extended to Azure Tables, Files, and Queues (previously available for Blobs).  
- User delegation SAS provides a more secure way to grant limited access to storage resources.  
- Unlike account or service SAS, user delegation SAS is signed by an Azure AD (Entra ID) identity rather than storage account keys.  
- Permissions granted by user delegation SAS cannot exceed those of the delegating identity.  
- User delegation SAS tokens have a maximum validity period of seven days.

**Definitions**  
- **User Delegation SAS**: A type of Shared Access Signature signed by an Azure AD identity, providing delegated and more secure access to storage services.  
- **Account/Service SAS**: SAS tokens signed by storage account keys, which have broad and powerful permissions.

**Key Facts**  
- User delegation SAS is now available for Tables, Files, and Queues in addition to Blobs.  
- User delegation SAS tokens can only be valid for up to seven days.  
- The SAS token’s permissions are limited by the permissions of the Azure AD identity that creates it.

**Examples**  
- None mentioned explicitly.

**Key Takeaways 🎯**  
- User delegation SAS enhances security by leveraging Azure AD identities instead of storage account keys.  
- It limits the scope and lifetime of access tokens, reducing risk.  
- Extending user delegation SAS to more storage services broadens secure access options across Azure Storage.

---

## AFS in Israel Central

**Timestamp**: 00:04:01 – 00:04:52

**Key Concepts**  
- Azure File Sync (AFS) enables synchronization of Windows File Server SMB shares via Azure File Shares in the cloud.  
- AFS allows local SMB shares to offload content to the cloud when running out of capacity, providing virtually unlimited storage.  
- Content that is offloaded appears available locally but is actually stored in the cloud and downloaded on-demand, which may cause increased latency.  
- Deploying the sync service in multiple locations reduces latency and helps meet data residency requirements.

**Definitions**  
- **Azure File Sync (AFS)**: A service that synchronizes SMB shares from Windows File Servers to Azure File Shares, enabling cloud-based storage extension and centralized file management.

**Key Facts**  
- Azure File Sync is now available in the Israel Central region.  
- Offloaded content is not stored locally but remains visible to users.  
- Accessing offloaded content triggers on-demand download, which can increase latency.  
- Multi-location sync service deployment reduces lag and supports data residency compliance.

**Examples**  
- A Windows File Server running out of SMB share capacity can offload files to Azure File Share, maintaining the appearance of local availability while freeing local storage.

**Key Takeaways 🎯**  
- Azure File Sync extends local file server storage capacity by leveraging cloud storage transparently.  
- Offloading files helps manage limited local storage but may introduce latency when accessing offloaded files.  
- Deploying sync services closer to users or in required regions improves performance and compliance.  
- Availability of AFS in Israel Central expands options for customers in that geography.

---

## ANF app volume group for Oracle data protection

**Timestamp**: 00:04:52 – 00:05:47

**Key Concepts**  
- Azure NetApp Files (ANF) app volume groups for Oracle support data protection volumes.  
- Oracle databases typically use multiple volumes (2 to 12) depending on size and configuration.  
- App volume groups create all necessary volumes following best practices.  
- Support for cross-zone and cross-region replication is available.  
- Replication sends only changed blocks to optimize data transfer.  
- Replication must currently be enabled via REST API.  
- The feature helps safeguard data against threats and disruptions, ensuring continuous availability.

**Definitions**  
- **App volume group for Oracle**: A collection of multiple volumes configured together to support an Oracle database environment, designed according to best practices.  
- **Data protection volume support**: Capability to replicate volumes for backup and disaster recovery purposes.  
- **Cross-zone and cross-region replication**: Replication of data across different availability zones or geographic regions to enhance resilience.

**Key Facts**  
- Oracle databases use between 2 to 12 volumes depending on size and configuration.  
- Replication transmits only changed blocks, improving efficiency.  
- Enabling replication currently requires use of the REST API.

**Examples**  
- None mentioned explicitly.

**Key Takeaways 🎯**  
- ANF app volume groups simplify managing multiple Oracle database volumes by automating best practice configurations.  
- Data protection via replication enhances resilience and availability of Oracle workloads on ANF.  
- Efficient replication reduces bandwidth by sending only changed data blocks.  
- Although currently enabled via REST API, this feature is aimed at helping customers protect their data continuously against disruptions.

---

## Azure Load Testing new region

**Timestamp**: 00:05:47 – 00:06:22

**Key Concepts**  
- Azure Load Testing is now available in a new region: Switzerland North.  
- It is a managed service designed for high-scale load testing using cloud resources.  
- Supports multiple testing methods including Apache JMeter, local scripts, and a web-based experience that can generate scripts automatically.  
- Provides detailed analytics to understand component behavior under stress and identify bottlenecks.

**Definitions**  
- **Azure Load Testing**: A managed cloud service that enables users to perform scalable load testing on applications, leveraging cloud infrastructure to simulate high traffic and analyze performance.

**Key Facts**  
- New region added: Switzerland North.  
- Testing methods supported: Apache JMeter, local scripts, web experience with script generation.  
- Analytics include stress testing results and component behavior insights.

**Examples**  
- Using Apache JMeter or local scripts to perform load tests.  
- Using the web experience to generate load testing scripts automatically.

**Key Takeaways 🎯**  
- Azure Load Testing’s expansion to Switzerland North increases regional availability and potentially reduces latency for users in that area.  
- The service’s flexibility in script usage and automatic script generation simplifies load testing setup.  
- Analytics provided help quickly identify performance bottlenecks, aiding in targeted optimization efforts.

---

## App Testing reporting

**Timestamp**: 00:06:22 – 00:07:08

**Key Concepts**  
- Azure App Testing now includes enhanced reporting features in General Availability (GA).  
- App Testing supports load testing and end-to-end flow testing.  
- Integration of Playwright Workspaces reporting for cloud-scale web testing.  
- Enhanced debugging reporting via storage account integration.  
- Use of a trace viewer in the Azure portal for deeper analysis of test reports.

**Definitions**  
- **Azure App Testing**: A service that provides load testing and end-to-end testing capabilities for applications, now with improved reporting features.  
- **Playwright Workspaces reporting**: Reporting functionality integrated into App Testing for detailed cloud-scale web testing results.  
- **Trace viewer**: A tool accessible through the Azure portal that allows detailed examination of test execution and reporting data stored in a specified storage account.

**Key Facts**  
- Reporting update for App Testing is now generally available (GA).  
- Debugging requires specifying a storage account to collect data.  
- Trace viewer enables interactive and detailed analysis of test data directly from the portal.

**Examples**  
- When debugging is enabled, test data is stored in a storage account, which can then be accessed and analyzed using the trace viewer in the Azure portal.

**Key Takeaways 🎯**  
- The new App Testing reporting features simplify debugging and analysis of load and end-to-end tests.  
- Storing debugging data in a storage account is essential for using the trace viewer.  
- Playwright Workspaces reporting enhances cloud-scale web testing capabilities within App Testing.  
- The trace viewer provides a user-friendly way to interact with detailed test reports without leaving the Azure portal.

---

## GitHub Copilot SDK

**Timestamp**: 00:07:08 – 00:07:41

**Key Concepts**  
- GitHub Copilot now offers an SDK (Software Development Kit).  
- The SDK allows integration of GitHub Copilot capabilities into custom applications and experiences.  
- Advanced features of GitHub Copilot remain available through the SDK, including multi-step planning, use of multiple AI models, leveraging MCP servers, and building custom agents.  
- The SDK provides flexibility to trigger GitHub Copilot functionality programmatically rather than only via CLI or VS Code integration.

**Definitions**  
- **GitHub Copilot SDK**: A software development kit that enables developers to embed GitHub Copilot’s AI-powered coding assistance into their own applications and workflows.

**Key Facts**  
- The SDK extends the use of GitHub Copilot beyond the traditional CLI and VS Code integrations.  
- Supports advanced capabilities such as multi-step planning and multiple model usage.  
- Enables building of custom agents and leveraging MCP (Model Control Plane) servers.

**Examples**  
- Using GitHub Copilot SDK within custom apps or personalized user experiences instead of just through VS Code or CLI.

**Key Takeaways 🎯**  
- GitHub Copilot SDK broadens how developers can access and utilize Copilot’s AI features.  
- It maintains all advanced functionalities, ensuring powerful AI assistance is available in any environment.  
- The SDK empowers developers to create tailored AI-driven coding tools and workflows beyond standard integrations.  

---

## Close

**Timestamp**: 00:07:41 – unknown

**Key Concepts**  
- Conclusion and closing remarks of the presentation/video.

**Definitions**  
- None introduced in this segment.

**Key Facts**  
- The speaker wraps up the session at this point.

**Examples**  
- None mentioned.

**Key Takeaways 🎯**  
- The session has ended.  
- The speaker hopes the content was useful.  
- A polite sign-off: "Until next video, take care."  

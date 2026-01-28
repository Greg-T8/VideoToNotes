### 🎤 [00:23:27 – 00:25:00] SSPR  
**Timestamp**: 00:23:27 – 00:25:00

**Key Concepts**  
- Self-Service Password Reset (SSPR) as a feature to enable users to reset their own passwords without help desk intervention.  
- Password write-back capability for hybrid identity environments, allowing password changes in the cloud to sync back to on-premises directories.  
- Licensing tiers (P1, P2) determine available features and user groups.  
- Configurable authentication methods and policies for password reset.  
- Role-based access control with emphasis on privileged roles like Global Administrator.

**Definitions**  
- **Self-Service Password Reset (SSPR)**: A feature that allows users to reset their own passwords securely without contacting IT support.  
- **Password Write-Back**: The process where password changes made in the cloud environment are written back to the on-premises directory in hybrid setups.  
- **Global Administrator**: The highest privileged role in Azure AD, with broad permissions, requiring strict control over assignment.

**Key Facts**  
- P1 license is required for SSPR with password write-back in hybrid identity scenarios.  
- Different licenses (P1, P2) can be assigned to different user groups based on their needs (e.g., privileged users may require P2 for privileged identity management).  
- Authentication methods for SSPR can be customized to require one or multiple verification methods, including custom questions.  
- Users are prompted to set up SSPR when they first join the organization and log in.  
- Role assignments can be delegated with specific permissions; privileged roles should be carefully assigned.

**Examples**  
- Privileged users might have P2 licenses for stronger identity protection and privileged identity management.  
- Basic workers might have P1 licenses with standard SSPR capabilities.  
- Password reset options can be configured per user or group, including how many authentication methods are required.

**Key Takeaways 🎯**  
- Implement SSPR to reduce help desk calls related to password resets.  
- Use password write-back to maintain synchronization between cloud and on-premises passwords in hybrid environments.  
- Assign licenses based on user roles and security needs; not all users require the same license level.  
- Configure authentication methods thoughtfully to balance security and usability.  
- Restrict assignment of highly privileged roles like Global Administrator to minimize security risks.
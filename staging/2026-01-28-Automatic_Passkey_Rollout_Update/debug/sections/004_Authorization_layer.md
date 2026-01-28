### 🎤 [00:03:52 – 00:04:43] Authorization layer  
**Timestamp**: 00:03:52 – 00:04:43

**Key Concepts**  
- Distinction between authentication (authN) and authorization (authZ) layers.  
- Passkeys focus on strong authentication (proving identity).  
- Authorization involves additional checks beyond authentication, such as device compliance and health.  
- Conditional Access policies can enforce authorization requirements like device management status.  
- Passkey strength is one factor within a broader authorization framework.

**Definitions**  
- **Authentication (AuthN)**: The process of proving who you are (e.g., using passkeys).  
- **Authorization (AuthZ)**: The process of determining what an authenticated user is allowed to do, often involving policy checks.  
- **Conditional Access**: A policy framework (e.g., in Microsoft Entra) that enforces additional requirements such as device management and health status before granting access.

**Key Facts**  
- Passkeys provide very strong authentication but do not by themselves guarantee authorization.  
- Conditional Access can require that a device be managed (e.g., by Intune) and healthy, in addition to having a strong credential like a passkey.  
- Even if a passkey is synced across multiple devices, access can be restricted based on authorization policies.

**Examples**  
- Conditional Access policy requiring a managed device (managed by Intune) and device health in addition to passkey authentication.

**Key Takeaways 🎯**  
- Passkeys improve authentication strength but must be combined with authorization policies to control access effectively.  
- Authorization policies like Conditional Access add layers of security by checking device compliance and health.  
- The existence of a strong credential (passkey) alone does not guarantee access; authorization checks remain essential.
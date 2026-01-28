### 🎤 [00:18:57 – 00:20:48] Devices  
**Timestamp**: 00:18:57 – 00:20:48

**Key Concepts**  
- Shift from traditional domain-joined devices to more flexible device management models.  
- Devices can be either **registered** or **joined** to the Entra tenant.  
- Registered devices are typically personal devices that need limited management and access to corporate resources.  
- Joined devices are corporate-owned and require full control and management.  
- Devices appear as objects within the Entra tenant and can be managed accordingly.  
- Licensing for Entra ID features can be assigned per user and vary by license level (e.g., P1, P2).  

**Definitions**  
- **Registered Device**: A device that is known to the Entra tenant, allowing some management and policy application, typically used for personal devices accessing corporate applications.  
- **Joined Device**: A corporate-owned device fully managed and controlled by the organization, allowing direct authentication with corporate accounts at login.  

**Key Facts**  
- Registered devices allow policy application and management via tools like Intune.  
- Joined devices enable users to log in directly with their corporate accounts (e.g., john@savilltech.net) at the device login screen.  
- Devices show up as objects in the Entra tenant for management purposes.  
- Entra licenses differ by functionality and can be bundled with Microsoft 365 plans (e.g., E5 includes P2 license, E3 includes P1 license).  
- VPN is no longer a strict requirement for device authentication or management due to direct interaction with the Entra tenant.  

**Examples**  
- Registering a personal device so it can access corporate applications while ensuring it is healthy and not jailbroken.  
- Joining a corporate device to allow full control and direct login with corporate credentials.  

**Key Takeaways 🎯**  
- Modern device management favors flexibility to support remote and mobile work scenarios without relying on VPNs.  
- Choosing between registering and joining devices depends on ownership and required control level.  
- Entra tenant integration allows centralized device visibility and management.  
- Licensing should be considered carefully as it impacts available features and management capabilities.
### 🎤 [00:08:24 – 00:09:54] Registration campaign change  
**Timestamp**: 00:08:24 – 00:09:54

**Key Concepts**  
- The registration campaign process is changing to incorporate passkeys instead of relying solely on SMS or phone calls.  
- Passkeys can be either device-bound or synced, depending on the configuration and user groups.  
- The registration campaign behavior adapts based on whether synced passkeys are enabled or not.  
- Existing configurations and targeting remain intact, with added granularity for different user groups.

**Definitions**  
- **Registration campaign**: A process that targets users to register authentication methods, previously via SMS or phone calls, now shifting to passkeys.  
- **Device-bound passkeys**: Passkeys stored locally on a device, typically used via Microsoft Authenticator.  
- **Synced passkeys**: Passkeys that are synchronized across devices, allowing broader access and management.

**Key Facts**  
- If only device-bound passkeys are used, the registration campaign will use Microsoft Authenticator.  
- If synced passkeys are available, the campaign will use passkeys that are synced.  
- The registration campaign setting can be enabled, Microsoft managed, or disabled:  
  - Enabled/Microsoft managed with synced passkeys → campaign uses passkeys.  
  - Enabled/Microsoft managed with device-bound only → campaign uses authenticator.  
  - Disabled → no changes or actions taken.  
- Passkeys are considered superior in security compared to previous methods.  
- Existing configurations are preserved; enabling passkeys does not automatically enable synced passkeys if attestation is required.  
- Admins can customize which groups get device-bound vs. synced passkeys (e.g., sensitive users vs. general workers).

**Examples**  
- Device-bound passkeys targeted to all users via Microsoft Authenticator.  
- Synced passkeys enabled only for specific groups, such as task-based workers.  
- Sensitive users can be assigned device-bound passkeys, while others get synced passkeys.

**Key Takeaways 🎯**  
- The registration campaign is evolving to prioritize passkeys over SMS/phone calls for authentication registration.  
- Passkeys provide enhanced security and flexibility in targeting different user groups.  
- Existing tenant configurations remain intact; changes enable more granular control rather than forcing a switch.  
- Admins should review and adjust their authentication method configurations post-enablement to optimize security and user experience.  
- Documentation and further details are available in the message center for administrators to consult.
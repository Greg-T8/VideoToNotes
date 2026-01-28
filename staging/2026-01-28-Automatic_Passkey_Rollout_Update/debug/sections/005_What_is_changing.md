### 🎤 [00:04:43 – 00:08:24] What is changing  
**Timestamp**: 00:04:43 – 00:08:24

**Key Concepts**  
- Transition from preview to default passkey profile management in Azure AD authentication methods.  
- Passkey profiles control device bound vs synced passkeys and attestation requirements.  
- Existing FIDO2 authentication method settings will drive the new default passkey profile configuration.  
- Attestation enabled means only device bound passkeys allowed; attestation disabled allows both device bound and synced passkeys.  
- Targeting and assignment of passkey profiles will honor existing group targeting and AA GUID configurations.  
- Multiple passkey profiles can be created and targeted to different groups for granular control.  
- Registration campaigns will shift from SMS/phone call targets to passkey-based authentication methods.

**Definitions**  
- **Passkey Profile**: A configuration entity that defines whether passkeys are device bound or synced and whether attestation is required.  
- **Attestation**: A security feature that verifies the authenticity of the device or credential; when required, synced passkeys are not allowed.  
- **Device Bound Passkey**: A passkey tied to a specific device, not synced across devices.  
- **Synced Passkey**: A passkey that can be synchronized across multiple devices for user convenience.  
- **Registration Campaign**: A process or policy that encourages or enforces users to register authentication methods, previously targeting SMS/phone calls, now moving to passkeys.

**Key Facts**  
- Current FIDO2 authentication method settings determine the default passkey profile behavior.  
- Timeline for rollout:  
  - Worldwide: Preview in March; automatic enablement April through May.  
  - GCC/GCC High/DoD: Enablement in April; automatic rollout in June.  
- If attestation is enabled, synced passkeys are disallowed; only device bound passkeys are permitted.  
- Existing targeting (groups, AA GUIDs) will be preserved and applied to the default passkey profile.  
- The enablement toggle for passkeys will disappear once fully rolled out, as passkeys become enabled for all users by default.

**Examples**  
- An organization can have a default device bound passkey profile for all users but create a separate synced passkey profile targeted only to specific groups.  
- Registration campaigns will now use Microsoft Authenticator for device bound passkeys and passkeys for synced scenarios instead of SMS or phone calls.

**Key Takeaways 🎯**  
- The new default passkey profile replaces previous manual passkey profile creation and management.  
- Attestation settings are critical in determining whether synced passkeys are allowed.  
- Administrators should review current FIDO2 attestation settings to understand how the default passkey profile will be configured.  
- Multiple passkey profiles allow flexible deployment strategies across different user groups.  
- Registration campaigns will evolve to promote passkey adoption, improving security and user experience.  
- The rollout timeline varies by environment, so plan accordingly for GCC and DoD tenants.
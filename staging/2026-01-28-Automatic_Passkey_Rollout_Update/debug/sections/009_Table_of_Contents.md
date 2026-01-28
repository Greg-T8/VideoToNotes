### 🎤 [00:00:00 – ??:??:??] Table of Contents  
**Timestamp**: 00:00:00 – unknown

**Key Concepts**  
- Passkeys provide phishing-resistant authentication by requiring device proximity.  
- Passkeys validate the domain name to prevent credential misuse on fraudulent sites.  
- Passkeys enable strong and fast authentication.  
- Synced passkeys allow the same passkey to be available across multiple devices within the same ecosystem.  
- Device-bound passkeys are tied to a single device and can support attestation.  
- Attestation is a cryptographic proof that a passkey is securely stored on trusted hardware.  
- Synced passkeys do not support attestation due to lack of a standard for multi-device attestation.  
- Authentication (AuthN) via passkeys is separate from authorization (AuthZ), which can be managed via conditional access policies.  
- Conditional access can enforce additional requirements such as device management and health status beyond just passkey authentication.  
- Passkey profiles in Entra allow configuration of device-bound vs synced passkeys and attestation requirements.  
- Existing FIDO2 attestation settings influence the default passkey profile configuration.

**Definitions**  
- **Passkey**: A modern authentication credential that is phishing-resistant and requires proximity of the authenticating device.  
- **Device-bound passkey**: A passkey stored on a single device, often with attestation proving its hardware security.  
- **Synced passkey**: A passkey that is synchronized across multiple devices within the same ecosystem (e.g., Apple or Android devices).  
- **Attestation**: A cryptographic signature from device hardware proving the authenticity and security of a passkey.  
- **Authentication (AuthN)**: The process of verifying identity (proving who you are).  
- **Authorization (AuthZ)**: The process of granting access rights after authentication, often managed by policies like conditional access.  
- **Conditional Access**: Security policies that enforce additional checks (device compliance, health, etc.) beyond authentication.

**Key Facts**  
- Passkeys require proximity via Bluetooth, NFC, or USB to authenticate.  
- Passkeys validate the exact domain name to prevent phishing (e.g., Microsoft.com vs microfiveof.com).  
- Synced passkeys can be used across devices in the same ecosystem but not across different ecosystems.  
- Attestation is not possible with synced passkeys due to the lack of a universal standard.  
- Entra’s passkey profiles can be configured to require attestation or allow syncing, but not both simultaneously.  
- The default passkey profile in Entra will be driven by existing FIDO2 attestation settings.

**Examples**  
- Using a passkey on a phone that must be near the authenticating device via Bluetooth or NFC.  
- Preventing phishing by ensuring a passkey for Microsoft.com cannot be used on a fake domain like microfiveof.com.  
- Synced passkeys available across all Apple devices (iPhone, iPad, Mac) or all Android devices.  
- Creating multiple passkeys: one on Apple ecosystem and one on Android ecosystem.  
- Conditional access requiring a managed and healthy device in addition to passkey authentication.

**Key Takeaways 🎯**  
- Passkeys significantly improve security by being phishing-resistant and requiring physical proximity.  
- Domain validation is a critical feature preventing credential theft via phishing sites.  
- Synced passkeys enhance user convenience but sacrifice attestation security guarantees.  
- Authentication strength via passkeys should be combined with authorization policies like conditional access for comprehensive security.  
- Administrators should understand the trade-offs between device-bound and synced passkeys when configuring Entra passkey profiles.  
- Existing FIDO2 attestation settings will influence how new passkey profiles behave by default.
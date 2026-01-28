### 🎤 [00:01:39 – 00:03:52] Synced and device-bound  
**Timestamp**: 00:01:39 – 00:03:52

**Key Concepts**  
- Difference between device-bound passkeys and synced passkeys  
- Device-bound passkeys are stored on a single device and can use attestation  
- Synced passkeys are shared across devices within the same ecosystem but lack attestation  
- Synced passkeys improve user convenience by being available on multiple devices  
- Attestation provides cryptographic proof of the passkey’s hardware origin and trustworthiness  
- Synced passkeys do not have a standardized attestation method due to multi-device presence  
- Passkeys focus on strong authentication (AuthN), while authorization (AuthZ) is handled separately (e.g., conditional access policies)

**Definitions**  
- **Device-bound passkey**: A passkey stored on a specific device (e.g., USB dongle, authenticator app) that cannot be synced to other devices and supports attestation.  
- **Synced passkey**: A passkey that is synchronized across multiple devices within the same ecosystem (e.g., Apple devices, Android devices) for easier access but without attestation.  
- **Attestation**: A cryptographic process that verifies a passkey is securely generated and stored on trusted hardware, validated by a root signing certificate (e.g., FIDO2).  
- **Authentication (AuthN)**: The process of proving one’s identity.  
- **Authorization (AuthZ)**: The process of determining access rights after authentication, often managed by policies like conditional access.

**Key Facts**  
- Synced passkeys are rolling out and will be available to all tenants in Entra.  
- Device-bound passkeys can be part of hardware security devices like USB dongles or authenticator apps on phones.  
- Synced passkeys sync only within a single ecosystem (Apple, Android, Chrome) and do not sync across different ecosystems.  
- Multiple passkeys can be created on different ecosystems (e.g., one on Apple, one on Android).  
- Attestation is not possible with synced passkeys due to lack of a universal standard for multi-device attestation.  
- Conditional access policies can require additional checks beyond passkey authentication, such as device management status.

**Examples**  
- Device-bound passkey stored on a USB dongle or authenticator app on a phone.  
- Synced passkeys available across all Apple devices (iPhones, iPads, Macs) or all Android devices or Chrome browsers within the same ecosystem.  
- Creating multiple passkeys: one on Apple devices and another on Android devices.

**Key Takeaways 🎯**  
- Synced passkeys enhance user convenience by allowing a single passkey to be used across multiple devices within the same ecosystem.  
- Device-bound passkeys offer stronger security guarantees through attestation but are limited to one device.  
- Lack of attestation in synced passkeys means some hardware-based trust assurances are missing.  
- Passkeys are focused on authentication; authorization and access control remain managed by policies like conditional access.  
- Users and administrators should understand the trade-offs between convenience (synced) and security (device-bound with attestation).
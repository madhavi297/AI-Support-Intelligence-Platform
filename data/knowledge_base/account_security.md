# Account Security and Authentication Guide

## Section 1: Password Reset and Expired Links
Users experiencing difficulty logging in should use the 'Forgot Password' link on the login page. 
Reset links are sent from no-reply@platform.com and expire after 15 minutes for security. If the reset email is not received, verify that corporate spam filters allow our domain, or request an administrator to trigger a manual password reset link from the Team Management console.

## Section 2: Account Lockout Policy
Accounts are automatically locked after 5 consecutive incorrect password attempts to protect against brute-force attacks. 
Locked accounts remain suspended for a 30-minute security cooldown. If immediate access is required for critical business operations, an organization primary administrator can unlock the account via Admin Console > Users > Unlock User. Support can also verify identity via telephone or authorized email domain.

## Section 3: Two-Factor Authentication (2FA) and Lost Devices
Two-factor authentication (2FA) is enforced via Time-based One-Time Password (TOTP) apps such as Google Authenticator, Authy, or 1Password. 
If an employee loses their 2FA device or recovery codes, the organization Super Admin can reset the user's 2FA credentials in the security dashboard. For sole administrator accounts without backup admins, a government-issued photo ID and corporate domain DNS ownership verification are required before support will manually reset 2FA.

## Section 4: Enterprise SSO and SAML Troubleshooting
Enterprise customers can configure SAML 2.0 Single Sign-On with identity providers including Okta, Azure Active Directory, and Google Workspace. 
The error code SAML_INVALID_ASSERTION typically indicates a clock skew greater than 5 minutes between the customer's IdP and our servers, or an expired x509 signing certificate in the SAML configuration. Verify that the assertion encryption and entity ID match the values provided in our SSO documentation.

## Section 5: Offboarding and User Revocation
When an employee leaves an organization, administrators should immediately navigate to Team Settings and select 'Revoke Access and Terminate Active Sessions'. 
This instantly invalidates all active JWT tokens, clears OAuth authorizations, and disconnects mobile devices. Deleted account data is archived according to your enterprise retention policy.

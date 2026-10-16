# General Support Policies, SLAs, and Compliance

## Section 1: Support Operating Hours and Response SLAs
Our global customer support team operates 24x7 for Urgent (Severity 1) production incidents. 
Standard support hours for High, Medium, and Low tickets are Monday through Friday, 8:00 AM to 8:00 PM EST. 
Guaranteed initial response times under Enterprise Service Level Agreements:
- Urgent (Severity 1): 1 hour initial response
- High (Severity 2): 4 hours initial response
- Medium (Severity 3): 24 hours initial response
- Low (Severity 4): 48 hours initial response

## Section 2: Security Certifications, SOC2, and HIPAA
Our cloud infrastructure is hosted in AWS SOC2 Type II and ISO 27001 audited data centers. 
We sign Business Associate Agreements (BAAs) for healthcare organizations requiring HIPAA compliance on our Enterprise plan. Prospective and current enterprise customers can request our latest SOC2 Type II audit report, third-party penetration test summary, and vendor risk questionnaire by contacting security-compliance@platform.com.

## Section 3: Data Retention and GDPR Compliance
Under EU General Data Protection Regulation (GDPR) and California Consumer Privacy Act (CCPA), customers have the right to request access to and deletion of personal data. 
Ticket transcripts and audit records are retained for 3 years by default for security audit purposes unless custom data retention periods (30, 90, or 365 days) are configured in Enterprise Organization Settings. Right-to-be-forgotten requests are fulfilled within 30 days.

## Section 4: On-Premise and Private Cloud Deployments
The platform is primarily delivered as a multi-tenant cloud SaaS. 
For defense, financial, and healthcare institutions with strict air-gapped data sovereignty mandates, we offer an on-premise containerized deployment package orchestrated via Kubernetes Helm charts or Docker Compose for AWS GovCloud and private OpenShift clusters.

## Section 5: Public API Documentation and Developer Tools
Developers can access our interactive OpenAPI Swagger UI documentation at /docs on our API gateway. 
We provide official SDKs for Python and TypeScript, as well as an importable Postman collection. Webhook testing endpoints are supported via CLI sandbox environments. Feature requests and roadmap votes can be submitted to roadmap.platform.com.

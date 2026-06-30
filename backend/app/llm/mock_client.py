class MockLLMClient:
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict | None = None,
    ) -> dict:
        return {
            "changelog": [
                {
                    "title": "Added Okta SSO support",
                    "summary": "Enterprise customers can configure Okta as a SAML identity provider for SSO.",
                    "evidence_ids": ["jira:AUTH-123", "github:pr-41", "github:pr-42"],
                },
                {
                    "title": "Added SSO audit logging",
                    "summary": "SSO login events now emit audit logs for successful and failed attempts.",
                    "evidence_ids": ["jira:AUTH-124", "github:pr-43"],
                },
                {
                    "title": "Improved SSO callback error handling",
                    "summary": "Invalid SAML responses and expired SSO callback requests now return clearer errors.",
                    "evidence_ids": ["jira:AUTH-125", "github:pr-42", "github:pr-44"],
                },
            ],
            "internal_release_notes": (
                "This release adds Okta SSO support with SAML configuration, audit logging "
                "for SSO login events, and improved callback error handling for invalid "
                "SAML responses and expired SSO requests."
            ),
            "customer_release_notes": (
                "Enterprise customers can now enable Okta Single Sign-On for streamlined "
                "authentication. SSO login errors are clearer when configuration or callback "
                "issues occur."
            ),
            "documentation_updates": [
                {
                    "doc_chunk_id": "doc:authentication.md#sso-configuration",
                    "doc_title": "Authentication Setup Guide",
                    "section": "SSO Configuration",
                    "suggested_change": "Add Okta-specific SAML setup instructions.",
                    "reason": "Okta SSO support changes the SSO setup flow for administrators.",
                    "evidence_ids": [
                        "jira:AUTH-123",
                        "github:pr-41",
                        "github:pr-42",
                        "doc:authentication.md#sso-configuration",
                    ],
                },
                {
                    "doc_chunk_id": "doc:enterprise_onboarding.md#identity-provider-setup",
                    "doc_title": "Enterprise Onboarding Guide",
                    "section": "Identity Provider Setup",
                    "suggested_change": "Document how enterprise admins enable Okta as an identity provider.",
                    "reason": "Enterprise onboarding now includes Okta SSO configuration.",
                    "evidence_ids": [
                        "jira:AUTH-123",
                        "github:pr-41",
                        "github:pr-42",
                        "doc:enterprise_onboarding.md#identity-provider-setup",
                    ],
                },
                {
                    "doc_chunk_id": "doc:troubleshooting_login.md#sso-login-failures",
                    "doc_title": "Troubleshooting Login Issues",
                    "section": "SSO Login Failures",
                    "suggested_change": (
                        "Add troubleshooting guidance for invalid SAML responses and expired "
                        "SSO callback requests."
                    ),
                    "reason": "SSO callback errors now provide clearer failure cases for support teams.",
                    "evidence_ids": [
                        "jira:AUTH-125",
                        "github:pr-42",
                        "github:pr-44",
                        "doc:troubleshooting_login.md#sso-login-failures",
                    ],
                },
            ],
            "evidence": [
                "jira:AUTH-123",
                "jira:AUTH-124",
                "jira:AUTH-125",
                "github:pr-41",
                "github:pr-42",
                "github:pr-43",
                "github:pr-44",
                "doc:authentication.md#sso-configuration",
                "doc:enterprise_onboarding.md#identity-provider-setup",
                "doc:troubleshooting_login.md#sso-login-failures",
            ],
        }

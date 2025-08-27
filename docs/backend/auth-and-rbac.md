# Authentication and RBAC

## Authentication

- OIDC（已选能力）：优先支持企业常用提供方（Keycloak/Auth0/Azure AD）
- JWT tokens; refresh flow as per provider
- Optional passwordless for limited roles if needed

## Authorization

- Role-based: SuperAdmin, SchoolAdmin, Scheduler, Teacher, Student, Viewer
- Resource-level checks with tenant scoping

## Session management

- Short-lived tokens; revocation via provider（与 OIDC 配置一致）
- CSRF protections for browser flows

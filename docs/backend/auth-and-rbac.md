# Authentication and RBAC

## Authentication

- OIDC providers: Keycloak/Auth0/Azure AD
- JWT tokens; refresh flow as per provider
- Optional passwordless for limited roles if needed

## Authorization

- Role-based: SuperAdmin, SchoolAdmin, Scheduler, Teacher, Student, Viewer
- Resource-level checks with tenant scoping

## Session management

- Short-lived tokens; revocation via provider
- CSRF protections for browser flows

# Cork API

Cork is being built as the backend foundation for a modern, organization-centric productivity platform. The long-term vision is to give teams one connected workspace for identity, work management, collaboration, knowledge, automation, analytics, and AI-assisted operations.

The product direction is inspired by the depth of enterprise platforms like Atlassian and Microsoft 365, the flexibility of Notion, and the developer-minded structure of modern SaaS systems. Cork should feel powerful enough for large organizations, but simple enough for small teams to adopt without needing a full operations department.

## Vision

Cork will be a multi-tenant SaaS platform where every major business object belongs to an organization. Users will be able to belong to multiple organizations, collaborate across teams, manage structured work, share knowledge, and use intelligent automation while keeping data ownership and permissions clear.

The platform is designed around a few core beliefs:

- Organizations are the center of the system.
- Authentication and authorization should be separate domains.
- Permissions must be scoped, auditable, and ready for enterprise use.
- Privacy, security, and maintainability should be first-class product features.
- Other applications should build on shared identity and organization models instead of inventing their own user logic.
- AI should assist real workflows, not sit beside the product as a disconnected feature.

## What Cork Will Become

Cork will grow into a modular productivity operating system for teams and companies. The API is structured around domain-driven Django apps so each major product area can evolve independently while sharing the same identity, tenancy, and security foundation.

Planned product domains include:

- Identity and access management for users, organizations, teams, memberships, roles, permissions, invitations, MFA, SSO, OAuth, magic links, and passkeys.
- Work management for projects, tasks, workflows, goals, scheduling, and operational planning.
- Collaboration for messaging, channels, meetings, notifications, presence, and activity streams.
- Knowledge management for documents, assets, internal wiki pages, and search.
- Intelligence features for AI assistance, automation, analytics, recommendations, and decision support.

## Architecture Direction

Cork API is a Django REST backend built with a multi-tenant, domain-oriented architecture. The system is intended to support PostgreSQL, UUID primary keys, soft deletion, audit fields, and clear ownership boundaries between apps.

The identity layer is the central source of truth. Other domains should reference identity and organization models rather than duplicating user, tenant, or permission logic.

The architecture is being shaped for:

- Enterprise readiness
- Extensibility
- Strong data boundaries
- Clear auditability
- Privacy-first defaults
- Future cloud, self-hosted, enterprise, and government deployment models

## Current Focus

The current backend foundation is focused on establishing the core platform primitives:

- Custom identity models
- Organization and membership structure
- Authentication primitives
- Scoped authorization models
- Environment-driven configuration
- PostgreSQL-backed Django settings
- A REST API foundation for future product endpoints

Cork is still early, but the foundation is being laid for a serious, scalable platform rather than a collection of isolated features.

-- FAIL-SAFE CREATE SCHEMA
CREATE SCHEMA IF NOT EXISTS "identity";

-- REQUIRED FOR gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- BEING TYPES
CREATE TABLE IF NOT EXISTS "identity"."being_types" (
    "id" SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "name" TEXT NOT NULL,
    "description" TEXT NOT NULL
);

INSERT INTO
    "identity"."being_types" ("name", "description")
SELECT 'HUMAN', 'Relating to or characteristic of humankind.'
UNION ALL
SELECT 'AGENT', 'An autonomous software program that perceives its environment, reasons, plans, and takes actions using tools to achieve specific goals without constant human supervision.';

-- BEING ROLES
CREATE TABLE IF NOT EXISTS "identity"."being_roles" (
    "id" SMALLINT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "name" TEXT NOT NULL,
    "description" TEXT NOT NULL
)
INSERT INTO
    identity.being_roles (name, description)
VALUES (
        'human.owner',
        'Primary human owner and administrator of the Atlas system'
    ),
    (
        'agent.orchestrator',
        'Central coordinating agent responsible for delegating tasks across Atlas'
    ),
    (
        'agent.team.lead',
        'Agent responsible for coordinating and supervising a specialized agent team'
    ),
    (
        'agent.team.member',
        'Worker agent responsible for executing assigned tasks'
    );

-- BEINGS
CREATE TABLE identity.beings (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    "being_type_id" SMALLINT NOT NULL,
    "being_role_id" SMALLINT NOT NULL,
    "name" TEXT NOT NULL,
    CONSTRAINT fk_identity_beings_being_type FOREIGN KEY ("being_type_id") REFERENCES "identity"."being_types" ("id"),
    CONSTRAINT fk_identity_beings_being_role FOREIGN KEY ("being_role_id") REFERENCES "identity"."being_roles" ("id")
);

INSERT INTO
    identity.beings (
        "being_type_id",
        "being_role_id",
        "name"
    )
VALUES (1, 1, 'Terry'),
    (2, 2, 'Atlas');
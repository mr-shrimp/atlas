CREATE SCHEMA IF NOT EXISTS "account";

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- USERS
CREATE TABLE IF NOT EXISTS account.users (
    "id" UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid (),
    "being_id" UUID NOT NULL,
    "username" TEXT NOT NULL UNIQUE,
    "email" TEXT NOT NULL UNIQUE,
    "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_account_users_being FOREIGN KEY ("being_id") REFERENCES "identity"."beings" ("id")
);

INSERT INTO
    account.users (
        "being_id",
        "username",
        "email"
    )
SELECT "id", 'txrry_x', 't.sikenaris@gmail.com'
FROM "identity"."beings"
WHERE
    being_type_id = 1
    AND being_role_id = 1;

-- PASSWORD CREDENTIALS
CREATE TABLE IF NOT EXISTS account.password_credentials (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    "user_id" UUID NOT NULL,
    "password_hash" TEXT NOT NULL,
    "algorithm" TEXT NOT NULL DEFAULT 'argon2id',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "revoked_at" TIMESTAMPTZ,
    CONSTRAINT fk_account_password_credentials_user FOREIGN KEY ("user_id") REFERENCES "account"."users" ("id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_password_credentials_user ON account.password_credentials (user_id);

INSERT INTO
    account.password_credentials (user_id, password_hash)
SELECT id, '$argon2id$v=19$m=16,t=2,p=1$NHR3ZXNkeTVlaHJlaDVodGQ$At2PUsKhlR1+f/cIL6Hlzw'
FROM account.users
WHERE
    username = 'txrry_x';

-- SESSIONS
CREATE TABLE IF NOT EXISTS account.sessions (
    "id" UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid (),
    "user_id" UUID NOT NULL,
    "token_hash" TEXT NOT NULL,
    "ip_address" INET,
    "user_agent" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "expires_at" TIMESTAMPTZ NOT NULL,
    "revoked_at" TIMESTAMPTZ,
    CONSTRAINT fk_account_sessions_user FOREIGN KEY ("user_id") REFERENCES "account"."users" ("id") ON DELETE CASCADE
);

-- PREFERENCE TYPES
CREATE TABLE IF NOT EXISTS account.preferences_types (
    "id" SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "key" TEXT NOT NULL UNIQUE,
    "description" TEXT NOT NULL,
    "data_type" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO
    account.preferences_types (key, description, data_type)
VALUES (
        'theme',
        'User interface theme',
        'string'
    ),
    (
        'notifications.enabled',
        'Enable notifications',
        'boolean'
    ),
    (
        'timezone',
        'User timezone',
        'string'
    ),
    (
        'dashboard.layout',
        'Dashboard layout configuration',
        'json'
    );

-- USER PREFERENCES
CREATE TABLE IF NOT EXISTS account.user_preferences (
    user_id UUID NOT NULL,
    preference_type_id SMALLINT NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    PRIMARY KEY (user_id, preference_type_id),
    CONSTRAINT fk_user_preferences_user FOREIGN KEY (user_id) REFERENCES account.users (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_preferences_type FOREIGN KEY (preference_type_id) REFERENCES account.preference_types (id)
);

INSERT INTO
    account.user_preferences (
        user_id,
        preference_type_id,
        value
    )
SELECT id, 1, 'dark'
FROM account.users
WHERE
    username = 'txrry_x'
ON CONFLICT (user_id, preference_type_id) DO
UPDATE
SET
    value = EXCLUDED.value,
    updated_at = NOW();
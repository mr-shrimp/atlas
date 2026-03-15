CREATE SCHEMA IF NOT EXISTS agents;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS agents.models (
    "id" SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "name" TEXT NOT NULL UNIQUE,
    "provider" TEXT NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO
    agents.models (name, provider, description)
VALUES (
        'gpt-5',
        'openai',
        'General purpose reasoning model'
    ),
    (
        'claude-sonnet',
        'anthropic',
        'Balanced reasoning and coding model'
    ),
    (
        'local-llm',
        'local',
        'Self-hosted language model'
    ),
    (
        'tool-only',
        'system',
        'Agent that executes tools without an LLM'
    );

CREATE TABLE IF NOT EXISTS agents.autonomy_levels (
    id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL UNIQUE,
    level SMALLINT NOT NULL,
    description TEXT NOT NULL
);

INSERT INTO
    agents.autonomy_levels (name, level, description)
VALUES (
        'manual',
        0,
        'Agent executes actions only when explicitly triggered by a user'
    ),
    (
        'assistant',
        1,
        'Agent assists with tasks but requires confirmation before execution'
    ),
    (
        'semi_autonomous',
        2,
        'Agent can perform limited actions independently'
    ),
    (
        'autonomous',
        3,
        'Agent operates independently and manages tasks proactively'
    );

CREATE TABLE IF NOT EXISTS agents.roles (
    id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO
    agents.roles (name, description)
VALUES (
        'orchestrator',
        'Central agent responsible for delegating and coordinating tasks across Atlas'
    ),
    (
        'department_head',
        'Agent responsible for managing a department within Atlas'
    ),
    (
        'team_lead',
        'Agent responsible for coordinating a specialized agent team'
    ),
    (
        'worker',
        'Agent responsible for executing assigned operational tasks'
    ),
    (
        'monitor',
        'Agent responsible for monitoring systems, alerts, and performance'
    );

CREATE TABLE IF NOT EXISTS agents.agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    being_id UUID NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    model_id SMALLINT NOT NULL,
    autonomy_level_id SMALLINT NOT NULL,
    role_id SMALLINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_agents_being FOREIGN KEY (being_id) REFERENCES identity.beings (id) ON DELETE CASCADE,
    CONSTRAINT fk_agents_model FOREIGN KEY (model_id) REFERENCES agents.models (id),
    CONSTRAINT fk_agents_autonomy FOREIGN KEY (autonomy_level_id) REFERENCES agents.autonomy_levels (id),
    CONSTRAINT fk_agents_role FOREIGN KEY (role_id) REFERENCES agents.roles (id)
);

INSERT INTO
    agents.agents (
        being_id,
        name,
        description,
        model_id,
        autonomy_level_id,
        role_id
    )
SELECT id, 'Atlas Orchestrator', 'Primary coordinating agent responsible for managing Atlas operations', 1, 3, 1
FROM identity.beings
WHERE
    name = 'Atlas';

CREATE TABLE IF NOT EXISTS agents.departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO
    agents.departments (name, description)
VALUES (
        'core',
        'Core Atlas infrastructure and orchestration'
    ),
    (
        'trading',
        'Market analysis and trading operations'
    ),
    (
        'news',
        'News collection and sentiment analysis'
    ),
    (
        'development',
        'Software development and engineering'
    ),
    (
        'analytics',
        'Data analysis and reporting'
    );

CREATE TABLE IF NOT EXISTS agents.teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    department_id UUID NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_teams_department FOREIGN KEY (department_id) REFERENCES agents.departments (id) ON DELETE CASCADE,
    CONSTRAINT uq_department_team UNIQUE (department_id, name)
);

INSERT INTO
    agents.teams (
        department_id,
        name,
        description
    )
SELECT id, 'orchestration', 'Core orchestration agents'
FROM agents.departments
WHERE
    name = 'core';

INSERT INTO
    agents.teams (
        department_id,
        name,
        description
    )
SELECT id, 'market_analysis', 'Agents analyzing market conditions'
FROM agents.departments
WHERE
    name = 'trading';

INSERT INTO
    agents.teams (
        department_id,
        name,
        description
    )
SELECT id, 'trade_execution', 'Agents responsible for executing trades'
FROM agents.departments
WHERE
    name = 'trading';

INSERT INTO
    agents.teams (
        department_id,
        name,
        description
    )
SELECT id, 'news_collection', 'Agents gathering global/local news'
FROM agents.departments
WHERE
    name = 'news';

INSERT INTO
    agents.teams (
        department_id,
        name,
        description
    )
SELECT id, 'engineering', 'Agents assisting with development tasks'
FROM agents.departments
WHERE
    name = 'devlopment';

CREATE TABLE IF NOT EXISTS agents.team_roles (
    id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO
    agents.team_roles (name, description)
VALUES (
        'lead',
        'Agent responsible for coordinating the team'
    ),
    (
        'member',
        'Standard agent responsible for executing tasks'
    ),
    (
        'specialist',
        'Agent with a specialized capability'
    ),
    (
        'observer',
        'Monitoring agent that observes team activity'
    ),
    (
        'backup',
        'Agent that replaces other agents if necessary'
    );

CREATE TABLE IF NOT EXISTS agents.team_members (
    team_id UUID NOT NULL,
    agent_id UUID NOT NULL,
    team_role_id SMALLINT NOT NULL,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (team_id, agent_id),
    CONSTRAINT fk_team_members_team FOREIGN KEY (team_id) REFERENCES agents.teams (id) ON DELETE CASCADE,
    CONSTRAINT fk_team_members_agent FOREIGN KEY (agent_id) REFERENCES agents.agents (id) ON DELETE CASCADE,
    CONSTRAINT fk_team_members_role FOREIGN KEY (team_role_id) REFERENCES agents.team_roles (id)
);

INSERT INTO
    agents.team_members (
        team_id,
        agent_id,
        team_role_id
    )
SELECT '522515cc-3db9-42cb-bd87-82e37e4e71e7', '55f254d6-7b19-4bc8-91b9-0c0059aece62', 1;

CREATE INDEX IF NOT EXISTS idx_team_members_agent ON agents.team_members (agent_id);

CREATE INDEX IF NOT EXISTS idx_teams_department ON agents.teams (department_id);

CREATE TABLE IF NOT EXISTS agents.task_statuses (
    id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO
    agents.task_statuses (name, description)
VALUES (
        'pending',
        'Task has been created but not yet queued'
    ),
    (
        'queued',
        'Task is waiting in the execution queue'
    ),
    (
        'running',
        'Task is currently being executed by an agent'
    ),
    (
        'completed',
        'Task completed successfully'
    ),
    (
        'failed',
        'Task execution failed'
    ),
    (
        'cancelled',
        'Task was cancelled before completion'
    ),
    (
        'retrying',
        'Task failed but will be retried'
    );

CREATE TABLE IF NOT EXISTS agents.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    created_by_agent_id UUID,
    assigned_agent_id UUID,
    title TEXT NOT NULL,
    description TEXT,
    payload JSONB,
    priority SMALLINT NOT NULL DEFAULT 1,
    status_id SMALLINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    scheduled_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    CONSTRAINT fk_tasks_creator FOREIGN KEY (created_by_agent_id) REFERENCES agents.agents (id),
    CONSTRAINT fk_tasks_assigned_agent FOREIGN KEY (assigned_agent_id) REFERENCES agents.agents (id),
    CONSTRAINT fk_tasks_status FOREIGN KEY (status_id) REFERENCES agents.task_statuses (id)
);

CREATE TABLE IF NOT EXISTS agents.task_queue (
    task_id UUID PRIMARY KEY,
    priority SMALLINT NOT NULL DEFAULT 1,
    queued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_task_queue_task FOREIGN KEY (task_id) REFERENCES agents.tasks (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS agents.task_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    task_id UUID NOT NULL,
    agent_id UUID NOT NULL,
    status_id SMALLINT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    result JSONB,
    error TEXT,
    CONSTRAINT fk_task_executions_task FOREIGN KEY (task_id) REFERENCES agents.tasks (id) ON DELETE CASCADE,
    CONSTRAINT fk_task_executions_agent FOREIGN KEY (agent_id) REFERENCES agents.agents (id),
    CONSTRAINT fk_task_executions_status FOREIGN KEY (status_id) REFERENCES agents.task_statuses (id)
);

CREATE TABLE IF NOT EXISTS agents.task_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    execution_id UUID NOT NULL,
    log_level TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_task_logs_execution FOREIGN KEY (execution_id) REFERENCES agents.task_executions (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON agents.tasks (status_id);

CREATE INDEX IF NOT EXISTS idx_task_queue_priority ON agents.task_queue (priority DESC);

CREATE INDEX IF NOT EXISTS idx_task_executions_task ON agents.task_executions (task_id);
-- Migration: create audit_entries table and append-only trigger
-- Note: run this against the development Postgres instance.

CREATE TABLE IF NOT EXISTS audit_entries (
    id BIGSERIAL PRIMARY KEY,
    audit_entry_id TEXT NOT NULL UNIQUE,
    event_id TEXT NOT NULL,
    category TEXT NOT NULL,
    visibility TEXT NOT NULL,
    redaction_level TEXT NOT NULL,
    summary TEXT NOT NULL,
    linked_ids TEXT[] DEFAULT ARRAY[]::TEXT[],
    payload JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Prevent updates/deletes to enforce append-only semantics
CREATE OR REPLACE FUNCTION prevent_audit_changes() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_entries are append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS prevent_audit_updates ON audit_entries;
CREATE TRIGGER prevent_audit_updates
    BEFORE UPDATE OR DELETE ON audit_entries
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_changes();

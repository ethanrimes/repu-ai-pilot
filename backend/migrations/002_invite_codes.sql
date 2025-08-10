-- backend/migrations/002_invite_codes.sql
BEGIN;

CREATE TABLE IF NOT EXISTS invite_codes (
  id          bigserial PRIMARY KEY,
  code        text NOT NULL UNIQUE,
  max_uses    integer NOT NULL DEFAULT 1,
  uses        integer NOT NULL DEFAULT 0,
  expires_at  timestamptz,
  created_by  bigint,
  redeemed_by bigint[],
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_invite_codes_expires_at ON invite_codes(expires_at);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_invite_codes_updated_at ON invite_codes;
CREATE TRIGGER trg_invite_codes_updated_at
BEFORE UPDATE ON invite_codes
FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

COMMIT;

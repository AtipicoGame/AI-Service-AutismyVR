-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Add new columns to chat_sessions
ALTER TABLE chat_sessions 
ADD COLUMN IF NOT EXISTS session_uuid UUID DEFAULT uuid_generate_v4(),
ADD COLUMN IF NOT EXISTS title VARCHAR(255),
ADD COLUMN IF NOT EXISTS mode VARCHAR(20) DEFAULT 'text',
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_session_uuid ON chat_sessions(session_uuid);
CREATE INDEX IF NOT EXISTS idx_mode ON chat_sessions(mode);

-- Add new columns to interactions
ALTER TABLE interactions
ADD COLUMN IF NOT EXISTS audio_response_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS liveportrait_data TEXT;

-- Update existing sessions to have UUIDs if they don't
UPDATE chat_sessions SET session_uuid = uuid_generate_v4() WHERE session_uuid IS NULL;

-- Set updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


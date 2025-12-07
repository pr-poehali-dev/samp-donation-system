CREATE TABLE IF NOT EXISTS donations (
    id SERIAL PRIMARY KEY,
    nickname VARCHAR(255) NOT NULL,
    amount INTEGER NOT NULL,
    card_number VARCHAR(19) DEFAULT '2200 7020 5523 2552',
    status VARCHAR(50) DEFAULT 'pending',
    telegram_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_donations_nickname ON donations(nickname);
CREATE INDEX idx_donations_status ON donations(status);
CREATE INDEX idx_donations_created_at ON donations(created_at DESC);
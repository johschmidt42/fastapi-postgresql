CREATE TABLE IF NOT EXISTS profession (
    id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    last_updated_at TIMESTAMP
);


CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS users
(
    id UUID PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    last_updated_at TIMESTAMP,
    profession_id UUID REFERENCES profession (id) NOT NULL
);


CREATE TABLE IF NOT EXISTS orders
(
    id UUID PRIMARY KEY,
    amount DECIMAL(9, 2) NOT NULL CHECK (amount >= 0 AND amount <= 1000000),
    payer_id UUID REFERENCES users (id) NOT NULL,
    payee_id UUID REFERENCES users (id) NOT NULL
);


CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    document JSONB,
    created_at TIMESTAMP NOT NULL,
    last_updated_at TIMESTAMP
);

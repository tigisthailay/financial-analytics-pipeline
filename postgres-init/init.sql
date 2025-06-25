-- postgres-init/init.sql

-- This will run automatically the first time container starts
--- Grant privileges to the user on the database
GRANT ALL PRIVILEGES ON DATABASE rate_db TO tegisty;

-- Connect to the new database
\c rate_db

-- Create custom schema (optional)
CREATE SCHEMA IF NOT EXISTS rate AUTHORIZATION tegisty;

-- Grant usage on the schema
GRANT USAGE, CREATE ON SCHEMA rate TO tegisty;

-- Create table
CREATE TABLE IF NOT EXISTS rate.exchange_rates (
  source TEXT,
  timestamp BIGINT,
  base_currency TEXT,
  target_currency TEXT,
  rate DOUBLE PRECISION
);

-- Grant  all permisions on table

GRANT ALL PRIVILEGES ON TABLE rate.exchange_rates TO tegisty;


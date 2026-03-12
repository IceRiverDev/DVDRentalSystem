-- Create a separate database for Keycloak
-- This runs before the dvdrental dump (00_ prefix ensures ordering)
SELECT 'CREATE DATABASE keycloak'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'keycloak')\gexec

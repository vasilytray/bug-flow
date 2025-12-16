#!/bin/bash
# backend/scripts/init-db.sh

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Создаем тестовую БД
    CREATE DATABASE bugflow_test;
    GRANT ALL PRIVILEGES ON DATABASE bugflow_test TO bugflow;
    
    -- Создаем расширения
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Настраиваем производительность
    ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
    ALTER SYSTEM SET pg_stat_statements.track = 'all';
    ALTER SYSTEM SET pg_stat_statements.max = 10000;
EOSQL
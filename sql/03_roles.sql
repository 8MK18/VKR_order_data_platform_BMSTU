-- Роли для промышленной эксплуатации
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'etl_writer') THEN
        CREATE ROLE etl_writer LOGIN PASSWORD 'etl_writer';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ml_reader') THEN
        CREATE ROLE ml_reader LOGIN PASSWORD 'ml_reader';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'mart_writer') THEN
        CREATE ROLE mart_writer LOGIN PASSWORD 'mart_writer';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'bi_reader') THEN
        CREATE ROLE bi_reader LOGIN PASSWORD 'bi_reader';
    END IF;
END $$;

-- ETL: запись в staging и dwh
GRANT USAGE ON SCHEMA staging, dwh TO etl_writer;
GRANT INSERT, UPDATE, DELETE, SELECT ON ALL TABLES IN SCHEMA staging TO etl_writer;
GRANT INSERT, UPDATE, DELETE, SELECT ON ALL TABLES IN SCHEMA dwh TO etl_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA staging, dwh TO etl_writer;

-- ML: чтение dwh
GRANT USAGE ON SCHEMA dwh TO ml_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA dwh TO ml_reader;

-- Mart writer: запись прогнозов
GRANT USAGE ON SCHEMA mart TO mart_writer;
GRANT INSERT, DELETE, SELECT ON mart.order_predictions TO mart_writer;
GRANT USAGE, SELECT ON SEQUENCE mart.order_predictions_prediction_id_seq TO mart_writer;

-- BI: только SELECT из mart
GRANT USAGE ON SCHEMA mart TO bi_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA mart TO bi_reader;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dwh;
CREATE SCHEMA IF NOT EXISTS mart;

CREATE TABLE IF NOT EXISTS staging.orders_raw (
    order_id BIGINT PRIMARY KEY,
    order_ts TIMESTAMP NOT NULL,
    customer_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    channel VARCHAR(30) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL,
    delivery_days INTEGER NOT NULL,
    customer_segment VARCHAR(30) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    order_status VARCHAR(30) NOT NULL,
    source_system VARCHAR(30) NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.web_products_raw (
    product_id BIGINT PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    web_rating NUMERIC(5,2),
    web_updated_at TIMESTAMP,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dwh.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    week INTEGER,
    day INTEGER
);

CREATE TABLE IF NOT EXISTS dwh.dim_customer (
    customer_key BIGSERIAL PRIMARY KEY,
    customer_id BIGINT UNIQUE NOT NULL,
    customer_segment VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS dwh.dim_product (
    product_key BIGSERIAL PRIMARY KEY,
    product_id BIGINT UNIQUE NOT NULL,
    product_name VARCHAR(255),
    category VARCHAR(100),
    web_rating NUMERIC(5,2)
);

CREATE TABLE IF NOT EXISTS dwh.dim_channel (
    channel_key SERIAL PRIMARY KEY,
    channel VARCHAR(30) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS dwh.fact_order (
    order_key BIGSERIAL PRIMARY KEY,
    order_id BIGINT UNIQUE NOT NULL,
    date_key INTEGER REFERENCES dwh.dim_date(date_key),
    customer_key BIGINT REFERENCES dwh.dim_customer(customer_key),
    product_key BIGINT REFERENCES dwh.dim_product(product_key),
    channel_key INTEGER REFERENCES dwh.dim_channel(channel_key),
    quantity INTEGER,
    unit_price NUMERIC(12,2),
    total_amount NUMERIC(14,2),
    delivery_days INTEGER,
    customer_segment VARCHAR(30),
    payment_method VARCHAR(30),
    order_status VARCHAR(30),
    source_system VARCHAR(30),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mart.order_predictions (
    prediction_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT,
    predicted_status VARCHAR(30),
    probability NUMERIC(8,6),
    model_version VARCHAR(100),
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW mart.v_order_dashboard AS
SELECT
    f.order_id,
    f.order_status,
    f.total_amount,
    f.delivery_days,
    f.quantity,
    f.customer_segment,
    f.payment_method,
    c.channel,
    p.category,
    p.product_name,
    p.web_rating,
    d.full_date
FROM dwh.fact_order f
JOIN dwh.dim_date d ON d.date_key = f.date_key
JOIN dwh.dim_channel c ON c.channel_key = f.channel_key
JOIN dwh.dim_product p ON p.product_key = f.product_key;

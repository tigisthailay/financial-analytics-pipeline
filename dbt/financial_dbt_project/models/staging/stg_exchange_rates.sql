-- dbt/models/staging/stg_exchange_rates.sql

WITH raw_data AS (
    SELECT * FROM rate.exchange_rates
)

SELECT 
    source,
    to_timestamp(timestamp) AS ts,
    base_currency,
    target_currency,
    rate
FROM raw_data

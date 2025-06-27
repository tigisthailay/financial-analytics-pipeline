{{ 
  config(
    materialized='incremental',
    unique_key='hash_key'
  ) 
}}

WITH raw_data AS (
    SELECT * FROM rate.exchange_rates
)

SELECT 
    md5(
      concat_ws(
        '||', 
        source, 
        timestamp, 
        base_currency, 
        target_currency, 
        rate
      )
    ) AS hash_key,
    source,
    to_timestamp(timestamp) AS ts,
    base_currency,
    target_currency,
    rate
FROM raw_data

{% if is_incremental() %}
    WHERE to_timestamp(timestamp) > (SELECT MAX(ts) FROM {{ this }})
{% endif %}

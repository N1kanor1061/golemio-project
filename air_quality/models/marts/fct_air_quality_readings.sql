{{
  config(
    materialized='incremental',
    unique_key=['station_id', 'pollutant', 'fetched_at']
  )
}}

select
    m.station_id,
    s.station_name,
    s.district,
    m.pollutant,
    m.value,
    m.averaged_hours,
    m.fetched_at,
    s.station_updated_at
from {{ ref('stg_air_quality_measurements') }} m
left join {{ ref('stg_air_quality_stations') }} s
    on m.station_id = s.station_id

{% if is_incremental() %}
where m.fetched_at > (select coalesce(max(fetched_at), '1900-01-01'::timestamptz) from {{ this }})
{% endif %}
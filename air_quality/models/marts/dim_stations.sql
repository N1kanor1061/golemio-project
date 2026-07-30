select
    station_id,
    station_name,
    district,
    latitude,
    longitude,
    station_updated_at
from {{ ref('stg_air_quality_stations') }}
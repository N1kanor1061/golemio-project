select
    m.station_id,
    s.station_name,
    s.district,
    m.pollutant,
    m.value,
    m.averaged_hours,
    s.station_updated_at
from {{ ref('stg_air_quality_measurements') }} m
left join {{ ref('stg_air_quality_stations') }} s
    on m.station_id = s.station_id
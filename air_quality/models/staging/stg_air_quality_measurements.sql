with latest as (
    select payload
    from raw_air_quality
    where fetched_at = (select max(fetched_at) from raw_air_quality)
),

features as (
    select jsonb_array_elements(payload -> 'features') as feature
    from latest
),

components as (
    select
        feature -> 'properties' ->> 'id' as station_id,
        jsonb_array_elements(feature -> 'properties' -> 'measurement' -> 'components') as component
    from features
)

select
    station_id,
    component ->> 'type' as pollutant,
    (component -> 'averaged_time' ->> 'value')::float as value,
    (component -> 'averaged_time' ->> 'averaged_hours')::int as averaged_hours
from components
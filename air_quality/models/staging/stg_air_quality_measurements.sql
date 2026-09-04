with snapshots as (
    select payload, fetched_at
    from raw_air_quality
),

features as (
    select
        jsonb_array_elements(payload -> 'features') as feature,
        fetched_at
    from snapshots
),

components as (
    select
        feature -> 'properties' ->> 'id' as station_id,
        jsonb_array_elements(feature -> 'properties' -> 'measurement' -> 'components') as component,
        fetched_at
    from features
)

select
    station_id,
    component ->> 'type' as pollutant,
    (component -> 'averaged_time' ->> 'value')::float as value,
    (component -> 'averaged_time' ->> 'averaged_hours')::int as averaged_hours,
    fetched_at
from components
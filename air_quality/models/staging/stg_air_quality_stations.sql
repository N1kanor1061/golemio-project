with latest as (
    select payload
    from raw_air_quality
    where fetched_at = (select max(fetched_at) from raw_air_quality)
),

features as (
    select jsonb_array_elements(payload -> 'features') as feature
    from latest
)

select
    feature -> 'properties' ->> 'id' as station_id,
    feature -> 'properties' ->> 'name' as station_name,
    feature -> 'properties' ->> 'district' as district,
    (feature -> 'geometry' -> 'coordinates' ->> 0)::float as longitude,
    (feature -> 'geometry' -> 'coordinates' ->> 1)::float as latitude,
    (feature -> 'properties' ->> 'updated_at')::timestamptz as station_updated_at
from features
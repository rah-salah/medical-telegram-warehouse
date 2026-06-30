with source as (
    select * from raw_image_detections
)
select
    id,
    message_id,
    lower(trim(channel_name)) as channel_name,
    image_path,
    lower(trim(detected_class)) as detected_class,
    confidence,
    bbox_x1, bbox_y1, bbox_x2, bbox_y2,
    detected_at
from source
where confidence is not null
  and confidence >= 0

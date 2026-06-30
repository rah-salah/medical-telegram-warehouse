with detections as (
    select * from {{ ref('stg_image_detections') }}
),

categorized as (
    select
        *,
        case
            when detected_class in ('bottle', 'cup', 'bowl', 'vase') then 'product_display'
            when detected_class in ('person', 'handbag', 'tie') then 'lifestyle'
            when detected_class in ('laptop', 'book', 'stop sign', 'tv') then 'promotional'
            else 'other'
        end as image_category
    from detections
),

joined as (
    select
        c.id as detection_id,
        c.message_id,
        c.channel_name,
        c.image_path,
        c.detected_class,
        c.confidence,
        c.image_category,
        c.bbox_x1, c.bbox_y1, c.bbox_x2, c.bbox_y2,
        f.message_date,
        f.views,
        f.forwards,
        f.has_media
    from categorized c
    left join {{ ref('fct_messages') }} f
        on c.message_id = f.message_id
)

select * from joined

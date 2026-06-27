with source as (
    select * from raw_telegram_messages
),
cleaned as (
    select
        message_id,
        lower(trim(channel_name)) as channel_name,
        message_date::timestamp as message_date,
        date(message_date) as message_day,
        coalesce(message_text, '') as message_text,
        length(coalesce(message_text, '')) as text_length,
        has_media,
        image_path,
        coalesce(views, 0) as views,
        coalesce(forwards, 0) as forwards
    from source
    where message_text is not null
)
select * from cleaned
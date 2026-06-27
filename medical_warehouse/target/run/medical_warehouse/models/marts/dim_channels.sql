
  
    

  create  table "medical_warehouse"."public"."dim_channels__dbt_tmp"
  
  
    as
  
  (
    with stg as (
    select * from "medical_warehouse"."public"."stg_telegram_messages"
)
select
    channel_name,
    count(*) as total_messages,
    sum(case when has_media then 1 else 0 end) as messages_with_images,
    avg(views) as avg_views,
    avg(forwards) as avg_forwards,
    min(message_date) as first_message_date,
    max(message_date) as last_message_date
from stg
group by channel_name
  );
  
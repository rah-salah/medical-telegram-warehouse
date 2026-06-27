
  
    

  create  table "medical_warehouse"."public"."fct_messages__dbt_tmp"
  
  
    as
  
  (
    with stg as (
    select * from "medical_warehouse"."public"."stg_telegram_messages"
)
select
    message_id,
    channel_name,
    message_date,
    message_day,
    message_text,
    text_length,
    has_media,
    image_path,
    views,
    forwards
from stg
  );
  
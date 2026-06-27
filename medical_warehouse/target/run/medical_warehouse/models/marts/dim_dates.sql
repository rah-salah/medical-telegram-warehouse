
  
    

  create  table "medical_warehouse"."public"."dim_dates__dbt_tmp"
  
  
    as
  
  (
    with dates as (
    select distinct
        date(message_date) as date_day
    from "medical_warehouse"."public"."stg_telegram_messages"
)
select
    date_day,
    extract(year from date_day)  as year,
    extract(month from date_day) as month,
    extract(day from date_day)   as day,
    extract(dow from date_day)   as day_of_week,
    to_char(date_day, 'Month')  as month_name,
    to_char(date_day, 'Day')    as day_name
from dates
order by date_day
  );
  
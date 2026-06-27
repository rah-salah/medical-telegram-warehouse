-- Custom test: all views should be >= 0
select *
from "medical_warehouse"."public"."fct_messages"
where views < 0
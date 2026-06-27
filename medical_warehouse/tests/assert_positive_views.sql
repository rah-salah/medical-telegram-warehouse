-- Custom test: all views should be >= 0
select *
from {{ ref("fct_messages") }}
where views < 0

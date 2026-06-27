
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Custom test: all views should be >= 0
select *
from "medical_warehouse"."public"."fct_messages"
where views < 0
  
  
      
    ) dbt_internal_test

    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select views
from "medical_warehouse"."public"."stg_telegram_messages"
where views is null



  
  
      
    ) dbt_internal_test
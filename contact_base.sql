select distinct ContactId
from dwh.crm_contactbase
where mobilephone in '7' || ('mobile_phone')
or mobilephone in SUBSTRING('mobile_phone', 2)
or mobilephone in '7' || SUBSTRING('mobile_phone', 2)

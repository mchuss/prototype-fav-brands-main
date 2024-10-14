select distinct itemid, brand_name_ax from dwh.flat_products fp
where brand_name_ax not in ''
and itemid in variable_itemids
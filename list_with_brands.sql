select distinct brand_id_ax, brand_name_ax from dwh.flat_products fp
where brand_id_ax in variable_brand_id_ax
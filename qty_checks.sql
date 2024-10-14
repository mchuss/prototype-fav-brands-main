WITH filtered_data AS (
    SELECT 
        c.crm_contact_id,
        f.brand_name_ax,
        c.qty / 1000 AS qty,
        c.itemid -- оставила itemid для джойн
    FROM 
        dwh.checks c
    LEFT JOIN 
        dwh.flat_products f ON c.itemid = f.itemid
    WHERE
        c.transdate BETWEEN today() - 365 AND today()
        AND c.itemid NOT IN (
            SELECT DISTINCT itemid
            FROM dwh.flat_products
            WHERE brand_name_ax IN ('Upakovka', 'usluga','goldapple')
        AND category_prices_name[2] IN (
            'Подарочные карты ЗЯ', 
            'Оборудование', 
            'Тестеры', 
            'Скидки консультантов', 
            'Подарки, семплы',
            'Goldapple'
        ))
        AND c.crm_contact_id = 'variable_customer_id'
),
filtered_products AS (
    SELECT 
        itemid, 
        brand_name_ax AS brand,
        category_prices_name[2] AS category1
    FROM 
        dwh.flat_products fp
    WHERE
        brand NOT IN ('Upakovka', 'usluga')
        AND category_prices_name[2] NOT IN (
            'Подарочные карты ЗЯ'
            ,'Оборудование'
            ,'Тестеры'
            ,'Скидки консультантов'
            ,'Подарки, семплы'
            ,'Goldapple'
        )
),
brand_category_totals AS (
    SELECT 
        fd.crm_contact_id,
        fd.brand_name_ax,
        fp.category1,
        SUM(fd.qty) AS total_qty
    FROM 
        filtered_data fd
    LEFT JOIN 
        filtered_products fp ON fd.itemid = fp.itemid -- джойн по itemid
    GROUP BY 
        fd.crm_contact_id, 
        fd.brand_name_ax,
        fp.category1
),
total_qty_per_contact AS (
    SELECT 
        crm_contact_id,
        SUM(total_qty) AS total_qty_sum
    FROM 
        brand_category_totals
    GROUP BY 
        crm_contact_id
)
SELECT 
    b.crm_contact_id,
    b.brand_name_ax,
    b.category1,
    b.total_qty,
    b.total_qty / t.total_qty_sum AS qty_share
FROM 
    brand_category_totals b
JOIN 
    total_qty_per_contact t ON b.crm_contact_id = t.crm_contact_id
ORDER BY
    b.total_qty DESC,
    b.crm_contact_id, 
    b.brand_name_ax,
    b.category1;
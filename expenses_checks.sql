WITH filtered_data AS (
    SELECT 
        c.crm_contact_id,
        f.brand_name_ax,
        c.amount / 100 AS amount,
        c.qty / 1000 AS qty
    FROM 
        dwh.checks c
    LEFT JOIN 
        dwh.flat_products f
    ON 
        c.itemid = f.itemid
    WHERE
        c.transdate BETWEEN today() - 365 AND today()
        AND c.itemid NOT IN (
            SELECT DISTINCT itemid
            FROM dwh.flat_products
            WHERE brand_name_ax IN ('Upakovka', 'usluga')
              AND arrayElement(category_prices_name, 2) NOT IN (
                  'Подарочные карты ЗЯ', 
                  'Оборудование', 
                  'Тестеры', 
                  'Скидки консультантов', 
                  'Подарки, семплы'
              )
              AND arrayElement(category_e_commerce_name, 2) NOT IN (
                  'Подарки, пробники,тестеры', 
                  'Упаковка. Не для ИМ'
              )
              AND category_e_commerce_name[2] NOT IN (
                  'Подарки, пробники, тестеры', 
                  'Упаковка. Не для ИМ', 
                  'Подарочные карты ЗЯ', 
                  'Вывод', 
                  'категория dummy'
              )
        )
        AND c.crm_contact_id = 'variable_customer_id'
),
brand_totals AS (
    SELECT 
        crm_contact_id,
        brand_name_ax,
        SUM(amount) AS total_amount,
        SUM(qty) AS total_qty
    FROM filtered_data
    GROUP BY 
        crm_contact_id, 
        brand_name_ax
),
overall_totals AS (
    SELECT
        crm_contact_id,
        SUM(total_amount) AS overall_amount
    FROM brand_totals
    GROUP BY crm_contact_id
)
SELECT 
    b.crm_contact_id,
    b.brand_name_ax,
    b.total_amount,
    b.total_qty,
    b.total_amount / o.overall_amount AS brand_share
FROM brand_totals b
JOIN overall_totals o
ON b.crm_contact_id = o.crm_contact_id
ORDER BY
    brand_share desc,
    b.crm_contact_id, 
    b.brand_name_ax
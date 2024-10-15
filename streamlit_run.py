import streamlit as st
import pandas as pd
from datetime import *
from pymongo import MongoClient
import clickhouse_connect
from settings import host_dwh, port, login, secret, mongo_connector
import time

start_date = "2020-01-01"


def load_df_galoc(file, replace_item):
    sql_query = (
        open(file, "r", encoding="utf8")
        .read()
        .replace("mobile_phone", replace_item)
        .replace("variable_customer_id", replace_item)
        .replace("variable_brand_id_ax", str(replace_item))
        .replace("variable_itemids", replace_item)
    )

    client = clickhouse_connect.get_client(
        host=host_dwh,
        port=port,
        username=login,
        password=secret,
    )

    raw_data = client.query(sql_query)
    df = pd.DataFrame(
        raw_data.result_rows, columns=[name for name in raw_data.column_names]
    )
    return df


def backend_simulation(mobile_phone):

    mongo_conn = mongo_connector
    client = MongoClient(mongo_conn)
    databases = [
        client["plaid_by_favourites"],
        client["plaid_ru_favourites"],
        client["plaid_kz_favourites"],
    ]

    df = load_df_galoc("contact_base.sql", mobile_phone)

    if df.empty:
        raise ValueError(
            f"Наверное, Вы не совершали заказов в Золотом Яблоке на номер: {mobile_phone}"
        )
    else:
        customer_id = str(df["ContactId"].iloc[0])

        ################################################################################################################
        st.markdown("---")
        st.markdown(
            "##### <span style='color:#dcff00'> Получаю список брендов, которые Вы добавили в 'Избранные бренды'</span>",
            unsafe_allow_html=True,
        )
        st.write(
            "Все добавленные бренды попадут в твой итоговый список любимых брендов с приоритетом 1"
        )
        ################################################################################################################

        for database in databases:
            collection = database["FavouriteBrands"]
            query = {"CustomerId": customer_id}
            df = pd.DataFrame(list(collection.find(query)))
            if not df.empty:

                df["CreatedDateTime"] = pd.to_datetime(df["CreatedDateTime"])
                df_filtered = df[df["CreatedDateTime"] > start_date]

                if not df_filtered.empty:

                    fav_brands_mongo = (
                        "("
                        + ", ".join(map(lambda x: f"'{x}'", df_filtered["Brand"]))
                        + ")"
                    )
                    fav_brands = fav_brands_mongo.to_list()
                    # fav_brands = load_df_galoc("list_with_brands.sql", fav_brands_mongo)

                    # fav_brands = (
                    #     fav_brands["brand_name_ax"].to_list()
                    #     if not fav_brands.empty
                    #     else []
                    # )

        time.sleep(2)
        ################################################################################################################
        st.markdown("---")
        st.markdown(
            "##### <span style='color:#dcff00'> Получаю список брендов, которые Вы добавили в 'Избранные товары'</span>",
            unsafe_allow_html=True,
        )
        st.write(
            "Все бренды избранных товаров попадут в твой итоговый список любимых брендов с приоритетом 3"
        )
        ################################################################################################################

        for database in databases:
            collection = database["FavouriteProducts"]
            query = {"CustomerId": customer_id}
            df = pd.DataFrame(list(collection.find(query)))

            if not df.empty:

                df["CreatedDateTime"] = pd.to_datetime(df["CreatedDateTime"])
                df_filtered = df[df["CreatedDateTime"] > start_date]

                if not df_filtered.empty:

                    fav_products_mongo = (
                        "("
                        + ", ".join(map(lambda x: f"'{x}'", df_filtered["Product"]))
                        + ")"
                    )
                    fav_products = load_df_galoc(
                        "list_with_products.sql", fav_products_mongo
                    )

                    fav_products = (
                        fav_products["brand_name_ax"].to_list()
                        if not fav_products.empty
                        else []
                    )

        time.sleep(2)
        ################################################################################################################
        st.markdown("---")
        st.markdown(
            "##### <span style='color:#dcff00'> Получаем список брендов по затратам клиента на бренд (60%)</span>",
            unsafe_allow_html=True,
        )
        st.write(
            """Теперь я возьму все твои заказы и проанализирую: на что ты больше всего тратил свои деньги."""
        )
        time.sleep(2)
        st.write("""Возьмем 60% всех твоих затрат за последние 2 года.""")
        time.sleep(2)
        st.write("""Нашел.""")
        time.sleep(2)
        st.write("""Исключаю категории бытовых трат.""")
        time.sleep(2)
        st.write(
            """Исключаю "тестовые" заказы. Товар бренда внутри одной категории, который тебе, видимо, не понравился, и больше ты его не захотел покупать"""
        )
        time.sleep(2)
        st.write("""Список получен""")

        ################################################################################################################

        expenses_checks = load_df_galoc("expenses_checks.sql", customer_id)
        expenses_checks["cumulative_share"] = expenses_checks["brand_share"].cumsum()
        expenses_checks_brands = list(
            expenses_checks[expenses_checks["cumulative_share"] <= 0.60][
                "brand_name_ax"
            ]
        )

        time.sleep(2)
        ################################################################################################################
        st.markdown("---")
        st.markdown(
            "##### <span style='color:#dcff00'> Получаем список брендов по количеству позиций внутри категорий (40%)</span>",
            unsafe_allow_html=True,
        )
        st.write(
            """Теперь я возьму все твои заказы и проанализирую: что ты покупал чаще всего"""
        )
        time.sleep(2)
        st.write("""Отсортировал по самым актуальным для тебя""")
        time.sleep(2)
        st.write(
            """Обнаружил список брендов от 40% всего количества приобретенного товара"""
        )
        time.sleep(2)
        st.write("""Снова исключаю "тестовые" заказы""")
        time.sleep(2)
        st.write("""Список получен""")
        ################################################################################################################

        qty_checks = load_df_galoc("qty_checks.sql", customer_id)
        qty_checks["cumulative_share"] = qty_checks["qty_share"].cumsum()
        qty_checks_brands = list(
            qty_checks[qty_checks["cumulative_share"] <= 0.60]["brand_name_ax"]
        )

        output = pd.DataFrame(
            fav_brands + expenses_checks_brands + qty_checks_brands + fav_products,
            columns=["Любимые бренды"],
        ).drop_duplicates(subset=["Любимые бренды"])

        st.success("Список брендов получен")

        return output


def main():

    st.title("Попробуем узнать Ваши любимые бренды?")

    st.markdown(
        """
    <style>
    div.stButton > button {
        background-color: grey;
        color: black !important;
        padding: 10px 24px;
        font-size: 14px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: all 2000ms;
    }
    div.stButton > button:hover {
        background-color: #bfff00;
        color: black !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    mobile_phone = st.text_input("Введите свой номер телефона:")

    if st.button("Отправить"):

        result = backend_simulation(mobile_phone)

        st.write("Ваши любимые бренды:")

        st.table(result)


if __name__ == "__main__":
    main()

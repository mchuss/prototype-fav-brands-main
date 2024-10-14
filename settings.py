from prefect.blocks.system import Secret

# ----------------------------------------------------------------------------
# clickhouse.ga.loc
# ----------------------------------------------------------------------------

HOST_CLICKHOUSE = Secret.load("shelf-host").get()
SERVICE_ACCOUNT_CLICKHOUSE_LOGIN = Secret.load("shelf-user").get()
SERVICE_ACCOUNT_CLICKHOUSE_SECRET = Secret.load("shelf-password").get()

login = SERVICE_ACCOUNT_CLICKHOUSE_LOGIN
secret = SERVICE_ACCOUNT_CLICKHOUSE_SECRET
host_dwh = HOST_CLICKHOUSE
port = 8123

conn_dwh = f"clickhouse://{login}:{secret}@{host_dwh}:{port}"
mongo_connector = Secret.load("mongo-conn").get()
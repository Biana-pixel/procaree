from psycopg2 import pool
from config import Config


# =====================================================
# POOL DE CONEXÕES COM O POSTGRESQL
# =====================================================

connection_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=5,
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    database=Config.DB_NAME,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD
)


# =====================================================
# PEGAR CONEXÃO
# =====================================================

def get_connection():
    return connection_pool.getconn()


# =====================================================
# DEVOLVER CONEXÃO
# =====================================================

def release_connection(conn):
    connection_pool.putconn(conn)
from dotenv import load_dotenv
import os
import psycopg2


def load_environment():
    """Load variables from a .env file if present."""
    load_dotenv()


def build_dsn_from_env(database: str, user_var: str, pw_var: str,
                        host_var: str = "PG_HOST", port_var: str = "PG_PORT") -> str:
    """Construct a PostgreSQL DSN from environment variables."""
    host = os.getenv(host_var, "localhost")
    port = os.getenv(port_var, 5432)
    user = os.getenv(user_var)
    password = os.getenv(pw_var)
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def build_kv_dsn(user: str, password: str, dbname: str,
                 host: str = "localhost", port: int | str = 5432) -> str:
    """Construct a key=value style DSN."""
    return f"dbname={dbname} user={user} password={password} host={host} port={port}"


def connect_using_env(database: str, user_var: str, pw_var: str,
                       host_var: str = "PG_HOST", port_var: str = "PG_PORT"):
    """Create a psycopg2 connection using env vars."""
    dsn = build_dsn_from_env(database, user_var, pw_var, host_var, port_var)
    return psycopg2.connect(dsn)

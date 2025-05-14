import duckdb
from langchain_community.vectorstores import DuckDB
from pathlib import Path

def get_vector_store(database_path: Path|str , table_name: str , embedding_model: str):
    """
    Get the vector store from the database path.
    """
    database_path = str(database_path)
    if not database_path.endswith(".db"):
        raise ValueError("database_path must end with .db")
    conn = duckdb.connect(database=database_path,
                          config={
                                  "enable_external_access": "false",
                                  "autoinstall_known_extensions": "false",
                                  "autoload_known_extensions": "false"
                              }
)
    return DuckDB(connection=conn ,table_name=table_name, embedding=embedding_model), conn
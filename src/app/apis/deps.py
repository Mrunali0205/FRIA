"""
Dependency definitions for FastAPI application.
"""
from typing import Annotated
from fastapi import Depends
from src.app.infrastructure.clients.sql_client import SQLClient

def get_sql_client():
    """
    Dependency to get an instance of SQLClient.
    """
    return SQLClient()

DBClientDep = Annotated[SQLClient, Depends(get_sql_client)]

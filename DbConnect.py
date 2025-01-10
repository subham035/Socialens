import os
from astrapy import DataAPIClient, Database

def connect_to_database() -> Database:
    """
    Connects to a DataStax Astra database.
    This function retrieves the database endpoint and application token from the
    environment variables `ASTRA_DB_API_ENDPOINT` and `ASTRA_DB_APPLICATION_TOKEN`.

    Returns:
        Database: An instance of the connected database.

    Raises:
        RuntimeError: If the environment variables `ASTRA_DB_API_ENDPOINT` or
        `ASTRA_DB_APPLICATION_TOKEN` are not defined.
    """
    endpoint = 'https://333fabb7-be16-40b2-8eb9-6ddcfe9ed97f-us-east-2.apps.astra.datastax.com'
    token = 'AstraCS:vykZGONKzcnqgOdmZdAtdHsJ:c2015367839f147873bc061939cae8430d40adc31d94f23a6d510efcc4c71ed8'

    if not token or not endpoint:
        raise RuntimeError(
            "Environment variables ASTRA_DB_API_ENDPOINT and ASTRA_DB_APPLICATION_TOKEN must be defined"
        )

    # Create an instance of the `DataAPIClient` class with your token.
    client = DataAPIClient(token)

    # Get the database specified by your endpoint.
    database = client.get_database(endpoint)

    print(f"Connected to database {database.info().name}")

    return database

connect_to_database();
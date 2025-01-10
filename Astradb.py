# import os
# from astrapy import DataAPIClient, Database

# def connect_to_database() -> Database:
#     """
#     Connects to a DataStax Astra database.
#     This function retrieves the database endpoint and application token from the
#     environment variables `ASTRA_DB_API_ENDPOINT` and `ASTRA_DB_APPLICATION_TOKEN`.

#     Returns:
#         Database: An instance of the connected database.

#     Raises:
#         RuntimeError: If the environment variables `ASTRA_DB_API_ENDPOINT` or
#         `ASTRA_DB_APPLICATION_TOKEN` are not defined.
#     """
#     

#     if not token or not endpoint:
#         raise RuntimeError(
#             "Environment variables ASTRA_DB_API_ENDPOINT and ASTRA_DB_APPLICATION_TOKEN must be defined"
#         )

#     # Create an instance of the `DataAPIClient` class with your token.
#     try:
#         print("Connecting to database...")
#         client = DataAPIClient(token)
#         database = client.get_database(endpoint)
#         print(f"Connected to database {database.info().name}")
#     except Exception as e:
#         print(f"Error connecting to database: {e}")

#     return database

# connect_to_database()

import os
import uuid
import pandas as pd
from astrapy import DataAPIClient, Database, Collection
from astrapy.constants import VectorMetric
from astrapy.info import CollectionVectorServiceOptions
import json

# Step 1: Connect to Astra Database
def connect_to_database() -> Database:
    """
    Connects to a DataStax Astra database using environment variables for the API endpoint and token.
    
    Returns:
        Database: The connected database instance.
    """
    #endpoint = os.environ.get("ASTRA_DB_API_ENDPOINT")  
    #token = os.environ.get("ASTRA_DB_APPLICATION_TOKEN")

    endpoint='https://333fabb7-be16-40b2-8eb9-6ddcfe9ed97f-us-east-2.apps.astra.datastax.com'
    token='=AstraCS:vykZGONKzcnqgOdmZdAtdHsJ:c2015367839f147873bc061939cae8430d40adc31d94f23a6d510efcc4c71ed8'

    if not token or not endpoint:
        raise RuntimeError(
            "Environment variables ASTRA_DB_API_ENDPOINT and ASTRA_DB_APPLICATION_TOKEN must be defined"
        )

    client = DataAPIClient(token)

    try:
        database = client.get_database(endpoint)
        print(f"Connected to database: {database.info().name}")
        return database
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

# Step 2: Create Collection in Astra Database
def create_collection(database: Database, collection_name: str) -> Collection:
    """
    Creates a collection in the specified database with vectorization enabled using Nvidia's NV-Embed-QA embedding model.
    
    Args:
        database (Database): The database instance where the collection will be created.
        collection_name (str): The name of the collection to create.
        
    Returns:
        Collection: The created collection.
    """
    collection = database.create_collection(
        collection_name,
        metric=VectorMetric.COSINE,
        service=CollectionVectorServiceOptions(
            provider="nvidia",
            model_name="NV-Embed-QA",
        ),
    )
    print(f"Created collection {collection.full_name}")
    return collection

# Step 3: Upload CSV Data to Astra Database
def upload_csv_data_to_db(database: Database, collection: Collection, csv_file_path: str) -> None:
    """
    Uploads data from a CSV file to the specified Astra collection.
    Each row in the CSV is processed, and a $vectorize field is added for embeddings.
    
    Args:
        database (Database): The database to insert data into.
        collection (Collection): The collection to upload the data to.
        csv_file_path (str): The path to the CSV file.
    """
    # Read CSV data into DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Add $vectorize field (you can customize this as per your needs)
    documents = [
        {
            **row.to_dict(),
            "$vectorize": f"summary: {row['topic']} | hashtags: {row['hashtags_used']}"
        }
        for _, row in df.iterrows()
    ]
    
    # Insert data into the collection
    inserted = collection.insert_many(documents)
    print(f"Inserted {len(inserted.inserted_ids)} items into the collection.")

# Step 4: Main Function to Connect, Create Collection, and Upload Data
def main():
    # Connect to Astra Database
    database = connect_to_database()

    # Create a new collection
    collection = create_collection(database, "social_media_collection")

    # Path to your CSV file
    csv_file_path = "next"

    # Upload data from CSV to the collection
    upload_csv_data_to_db(database, collection, csv_file_path)

if __name__ == "__main__":
    main()


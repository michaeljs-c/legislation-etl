import logging
import json
import pyodbc
import azure.functions as func
from azure.storage.blob import ContainerClient, BlobClient
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from .etl import etl, create_tables
import re
import os

logging.basicConfig(level=logging.INFO)

def run_etl():
    key_vault_name = "cube-key-vault"
    kv_uri = f"https://{key_vault_name}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_uri, credential=credential)

    blob_conn_container = "cube-data"
    blob_conn_str = client.get_secret("blobconnectionstring").value

    blob_container = ContainerClient.from_connection_string(conn_str=blob_conn_str, container_name=blob_conn_container)

    blob_list = blob_container.list_blobs()

    db_conn_str = client.get_secret("dbconnectionstring2").value
    conn = pyodbc.connect(db_conn_str)
    cursor = conn.cursor()
    create_tables(cursor, os.path.join("trigger_etl", "create_tables.sql"))
    conn.commit()
    re_sub = re.compile('&\w+;')

    for blob in blob_list:
        logging.info(f"Processing file {blob['name']}")

        blob = BlobClient.from_connection_string(conn_str=blob_conn_str, container_name=blob_conn_container, blob_name=blob['name'])
        blob_data = blob.download_blob().readall()
        json_data = blob_data.decode('utf-8')
        data = json.loads(json_data)

        etl(data, cursor, re_sub)

    conn.commit()
        

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This test HTTP triggered function executed successfully.")
    
    func = req.params.get('function')
    if not func:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            func = req_body.get('function')

    if func == "etl":
        logging.info("Running ETL!")
        run_etl()
        
        return func.HttpResponse(
             "This HTTP triggered function executed successfully.",
             status_code=200
        )
    else:
        return func.HttpResponse(f"This test HTTP triggered function executed successfully.")

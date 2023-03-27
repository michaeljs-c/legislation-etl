import logging
import json
import pyodbc
import azure.functions as func
from azure.storage.blob import ContainerClient, BlobClient
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from .etl import etl, execute_sql_file
import re
import os

logging.basicConfig(level=logging.INFO)

KEY_VAULT_NAME = "cube-key-vault"
BLOB_CONN_CONTAINER = "cube-data"
DB_CONN_STR_NAME = "dbconnectionstring2"
BLOB_CONN_STR_NAME = "blobconnectionstring"

def run_etl(drop_data:bool = False) -> None:
    """
    Run Azure ETL using secrets connection strings to access blob data and SQL Server

    args:
        drop_data: Recreates tables without running ETL
    """

    kv_uri = f"https://{KEY_VAULT_NAME}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_uri, credential=credential)

    db_conn_str = client.get_secret(DB_CONN_STR_NAME).value
    conn = pyodbc.connect(db_conn_str, autocommit=True)
    cursor = conn.cursor()

    execute_sql_file(cursor, os.path.join("trigger_etl", "create_tables.sql"))
    execute_sql_file(cursor, os.path.join("trigger_etl", "stored_procedures.sql"), sep="GO")

    if drop_data:
        logging.info("Dropping data from tables")
        return

    blob_conn_str = client.get_secret(BLOB_CONN_STR_NAME).value

    blob_container = ContainerClient.from_connection_string(conn_str=blob_conn_str, container_name=BLOB_CONN_CONTAINER)
    blob_list = blob_container.list_blobs()

    re_sub = re.compile('&\w+;')

    for blob in blob_list:
        logging.info(f"Processing file {blob['name']}")

        blob = BlobClient.from_connection_string(conn_str=blob_conn_str, container_name=BLOB_CONN_CONTAINER, blob_name=blob['name'])
        blob_data = blob.download_blob().readall()
        json_data = blob_data.decode('utf-8')
        data = json.loads(json_data)

        etl(data, cursor, re_sub)
        

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
        html = f"<html><body><h1>Hello, {name}!</h1></body></html>"
        return func.HttpResponse(html, mimetype="text/html", status_code=200)
    
    function = req.params.get('function')
    if not function:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            function = req_body.get('function')

    if function == "etl":
        logging.info("Running ETL!")
        try:
            run_etl()
        except Exception as e:
            logging.error(e)
            return func.HttpResponse("500 Internal Error", status_code=500)    

        html = "<html><body><h1>ETL executed successfully!</h1></body></html>"
        return func.HttpResponse(html, mimetype="text/html", status_code=200)
        
    elif function == "drop":
        logging.info("Dropping database")
        try:
            run_etl(drop_data=True)
        except Exception as e:
            logging.error(e)
            return func.HttpResponse("500 Internal Error", status_code=500)    
        
        html = "<html><body><h1>Data dropped successfully! Query the data to check.</h1></body></html>"
        return func.HttpResponse(html, mimetype="text/html", status_code=200)
    url = "https://cube-etl.azurewebsites.net/api/trigger_etl?"
    html = """
    <html>
        <head>
            <title>CUBE ETL - Azure Function</title>
        </head>
        <body>
            <h1>Welcome to the Azure Function!</h1>
            <p>Please choose a function:</p>
            <ul>
                <li><a href="{}">../trigger_etl?function=etl</a> - Start the ETL process</li>
                <li><a href="{}">../trigger_etl?function=drop</a> - Delete the database</li>
                <li><a href="{}">../trigger_etl?name=John</a> - Say hello</li>
            </ul>
        </body>
    </html>
    """.format(url + "function=etl", url + "function=drop", url + "name=John")

    return func.HttpResponse(html, mimetype="text/html")

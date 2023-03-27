import json
import pyodbc
import time
import os
import html
from bs4 import BeautifulSoup
import re
import logging
from typing import Tuple
from .insert_queries import LEGISLATION_QUERY, LEGISLATION_VERSION_QUERY, JURISDICTION_QUERY, ISSUING_BODY_QUERY, PART_QUERY

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_db_connection(driver: str, server: str, username: str, password: str, database: str = None) -> Tuple[pyodbc.Connection, pyodbc.Cursor]:    
    if database:
        conn = pyodbc.connect(
            f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
        )
    else:
        conn = pyodbc.connect(
            f"DRIVER={driver};SERVER={server};UID={username};PWD={password};TrustServerCertificate=yes;", autocommit=True
        )
    cursor = conn.cursor()
    return conn, cursor


def create_database(driver, server, database, username, password) -> None:
    conn, cursor = create_db_connection(driver=driver, server=server, username=username, password=password)
    try:
        cursor.execute(f"CREATE DATABASE {database}")
    except Exception as e:
        logger.info(str(e))
    conn.close()


def drop_database(driver, server, database, username, password) -> None:
    conn, cursor = create_db_connection(driver=driver, server=server, username=username, password=password)
    try:
        cursor.execute(f"DROP DATABASE {database}")
    except Exception as e:
        logger.info(str(e))
    conn.close()    


def execute_sql_file(cursor: pyodbc.Cursor, sql_file_path: str, sep=None) -> None:
    with open(sql_file_path) as f:
        queries = f.read()
        if sep:
            query_list = queries.split(sep)
            for q in query_list:
                cursor.execute(q)
        else:
            cursor.execute(queries)


def strip_html(string: str, re_sub_entities: re.Pattern=None):
    # unescape HTML entities
    unescaped_string = html.unescape(string)
    # strip HTML tags
    soup = BeautifulSoup(unescaped_string, 'html.parser')
    stripped_string = soup.get_text()
    # strip any remaining entities
    if re_sub_entities:
        stripped_string = re_sub_entities.sub('', stripped_string)

    return stripped_string


def etl(data: dict, cursor: pyodbc.Cursor, re_sub: re.Pattern):
    """
    Runs ETL for a given SQL Serer cursor

    args:
        data: parsed data dictionary containing legislation data
        cursor: database cursor object already instantiated
        re_sub: re pattern already compiled for better performance, used to strip content of html entities
    """

    # insert legislation
    item = data[0]
    cursor.execute(
        LEGISLATION_QUERY,
        item["LegislationSourceId"],
        item["Title"],
        item["NativeTitle"],
        item["JurisdictionSourceId"],
        item["IssuingBodySourceId"],
    )
    cursor.execute(
        LEGISLATION_VERSION_QUERY,
        item["LegislationSourceId"],
        item["LegislationVersionOrdinal"],
        item["LegislationVersionId"],
    )
    cursor.execute(
        JURISDICTION_QUERY, item["JurisdictionSourceId"], item["JurisdictionName"]
    )
    cursor.execute(
        ISSUING_BODY_QUERY, item["IssuingBodySourceId"], item["IssuingBodyName"]
    )
    # insert all parts
    for item in data:
        cursor.execute(
            PART_QUERY,
            item["PartSourceId"],
            item["PartVersionId"],
            item["PartVersionOrdinal"],
            item["LegislationSourceId"],
            item["LegislationVersionOrdinal"],
            item["ParentPartSourceId"],
            item["ParentPartVersionId"],
            item["ParentPartVersionOrdinal"],
            item["OrderNum"],
            item["Content"],
            strip_html(item["Content"], re_sub),
            item["NativeContent"],
            strip_html(item["NativeContent"]) if item["NativeContent"] is not None else None
        )


def get_files(path: str) -> list:
    return [os.path.join(path, n) for n in os.listdir(path)]


def local_run(driver: str, server: str, database: str, username: str, password: str, legislation_path="legislation_etl") -> None:
    """
    Local Execution of legislation ETL

    args:
        driver: The name of the ODBC driver to use (e.g. 'ODBC Driver 17 for SQL Server').
        server: The name or IP address of the server hosting the database (use host IP if using docker service).
        database: The name of the database to connect to.
        username: The username to use for authentication.
        password: The password to use for authentication.
    """
        
    logger.info("Connecting...")
    create_database(driver, server, database, username, password)

    conn, cursor = create_db_connection(driver, server, username, password, database)
    # cursor.fast_executemany = True
    logger.info("Connected")

    curr_directory = os.path.dirname(os.path.realpath(__file__))
    execute_sql_file(cursor, os.path.join(curr_directory, "create_tables.sql"))
    execute_sql_file(cursor, os.path.join(curr_directory, "stored_procedures.sql"), sep="GO")
    
    logger.info("Running etl")
    start = time.time()
    re_sub = re.compile('&\w+;')
    files = get_files(legislation_path)

    for file in files:
        logger.info(f"Processing file: {file}")
        with open(file) as f:
            try:
                data = json.load(f)
                etl(data, cursor, re_sub)
            except json.decoder.JSONDecodeError as e:
                logger.error(f"Could not process file {file}. Error: {e}")
    conn.commit()
    conn.close()
    logger.info(f"Total time: {time.time() - start}")

    
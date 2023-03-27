FROM python:3.9

RUN pip install pyodbc bs4

WORKDIR /app

COPY . /app
# COPY etl.py .
# COPY insert_queries.py .
# COPY create_tables.sql .
# COPY legislation_files ./legislation_files
# COPY setup_odbc.sh .
RUN chmod +x setup_odbc.sh
RUN bash -c "./setup_odbc.sh"

ENTRYPOINT [ "python", "local_etl_cli.py" ]
# ENTRYPOINT [ "bash" ]

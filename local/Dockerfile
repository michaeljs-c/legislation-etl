FROM python:3.9

RUN pip install pyodbc bs4

WORKDIR /app

COPY . /app
RUN chmod +x setup_odbc.sh
RUN bash -c "./setup_odbc.sh"

ENTRYPOINT [ "python", "local_etl_cli.py" ]

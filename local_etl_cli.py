import argparse
from trigger_etl.etl import local_run


if __name__ == '__main__':
    """
    Local Execution
    """

    DRIVER = "{ODBC Driver 18 for SQL Server}"
    SERVER = "(local)"
    DATABASE = "legislation"
    USERNAME = "sa"
    FILESDIR = "/app/legislation_files"

    parser = argparse.ArgumentParser(description='Local ETL for legislation to Sql Server')
    parser.add_argument('-D', '--driver', help='SQL Server driver string', default=DRIVER)
    parser.add_argument('-S', '--server', help='SQL Server server IP address (use host IP if using SS container)', default=SERVER)
    parser.add_argument('-d', '--database', help='Database name', default=DATABASE)
    parser.add_argument('-U', '--username', help='Database username', default=USERNAME)
    parser.add_argument('-P', '--password', help='Database password', required=True)
    parser.add_argument('-f', '--legislation_path', help='Directory containing legislation files', default=FILESDIR)

    args = parser.parse_args()

    local_run(
        **vars(args)
    )

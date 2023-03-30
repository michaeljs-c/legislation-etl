# Cube ETL assignment
Notes recorded during development process.

1. Define data models
    1. Legislation
    2. Jurisdiction
    3. Body
    4. Part
2. Set up SQL Server
3. ETL
    - Parse json
    - Insert to DB
4. Dockerise
5. Shift to cloud


Run SQL Server container
```sh
# userid = 'sa'
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=<password>" -p 1433:1433 -d mcr.microsoft.com/mssql/server:2022-latest
```

Install sqlcmd on linux
```sh
sudo apt install curl
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list
sudo apt-get update
sudo apt-get install mssql-tools unixodbc-dev
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc
```
<!-- CREATE TABLE Persons (PersonID int,LastName varchar(255),FirstName varchar(255),Address varchar(255),City varchar(255)); -->

Reset linux clock
```sh
sudo hwclock --hctosys
```

Connect to local db
```sh
sqlcmd -U sa -P <password> -H localhost -Q "create database legistlation" -S "(local)"
sqlcmd -U sa -P <password> -H localhost -i create_tables.sql -d legislation -S "(local)"
```
Build and run app
```sh
docker build -t cube-etl .
docker build --no-cache -t cube-etl .
docker run -it cube-etl
```

Azure steps
1. Setup sql server
2. Setup blob bucket
3. Setup Azure function
4. Get credentials string / secrets for function
5. Write stored procedure, query

Azure setup
VS Code Extensions
1. Azure Resources
2. Azure Functions

Venv for app
```sh
sudo apt-get install python3-venv
```

Setup Azure core tools
```sh
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4
```

Setup Azure CLI
```sh
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

Setup new function
```sh
func init legistlation_etl --worker-runtime python
func new --template "Http Trigger" --name trigger_etl --worker-runtime python
func azure functionapp publish cube-etl
```

Build and run app
```sh
docker build -f local/Dockerfile -t cube-etl .
docker run -v legislation_files:/app/legislation_files -it cube-etl -P <password> -S <IP address> -U sa
python3 local_etl_cli.py -P <password> -S <IP address> -U sa -f legislation_files
```
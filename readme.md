# Cube ETL assignment

1. Define data models
    1. Legislation
    2. Jurisdiction
    3. Body
    4. Part
2. Set up postgres
3. ETL
    - Parse json
    - Insert
4. Dockerise
5. Shift to cloud


```sh
docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="legislation" \
    -v $(pwd)/data:/var/lib/postgresql/data \
    -p 5432:5432 \
    --name pg-database \
    postgres:13
```

```sh
# userid = 'sa'
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=rootPassword1" -p 1433:1433 -d mcr.microsoft.com/mssql/server:2022-latest
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

sudo hwclock --hctosys

sqlcmd -U sa -P rootPassword1 -H localhost -Q "create database legistlation" -S "(local)"
sqlcmd -U sa -P rootPassword1 -H localhost -i create_tables.sql -d legislation -S "(local)"

docker build -t cube-etl .
docker build --no-cache -t cube-etl .
docker run -it cube-etl


1. Setup sql server
2. Setup bucket
3. Setup function
4. Get credentials string / secrets for function
5. Write stored procedure, query


Azure setup

Extensions
1. Azure Resources
2. Azure Functions

Venv
sudo apt-get install python3-venv


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

Setup function
```sh
func init legistlation_etl --worker-runtime python
func new --template "Http Trigger" --name trigger_etl --worker-runtime python
```
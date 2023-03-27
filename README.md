# Cube ETL Assignment

## Directory structure
1. legislation_files - contains json files with legislation data
2. local - files for building and running local dockerised app
3. trigger_etl - core assignment files
    - azure_etl.py - Azure app entry point
    - etl.py - core functionality for both azure and local deployment

## Running the application locally

Bringing up SQL Server:
```sh
cd local
docker-compose up
```
Building the app image (this was developed on linux machine, no guarentee to work on Windows, if any issues call the CLI with python instead):
```
docker build -f local/Dockerfile -t cube-etl .
```

Running the app:
```sh
# Running docker container (volume for data access -v <dir of data files>:/app/legislation_files)
docker run -v legislation_files:/app/legislation_files -it cube-etl -P rootPassword1 -S 172.21.0.1 -U sa
# Running without docker
python3 local_etl_cli.py -P rootPassword1 -S 172.21.0.1 -U sa -f legislation_files
```

Checking the app CLI params:
```sh
python3 local_etl_cli.py --help
docker run -it cube-etl --help
```


## Azure Function API

To Run the ETL:
```py
import requests

url = "https://cube-etl.azurewebsites.net/api/trigger_etl?function=etl"
response = requests.get(url)
print(response.content)

```
To drop the database:

```py
import requests

url = "https://cube-etl.azurewebsites.net/api/trigger_etl?function=drop"
response = requests.get(url)
print(response.content)
```

To say hello:

```py
import requests

url = "https://cube-etl.azurewebsites.net/api/trigger_etl?name=John"
response = requests.get(url)
print(response.content)
```

## Querying the database

1. **search_legislation** (minimum params = 1): Searches legislation parts based on 4 optional criteria:
    - Jurisdiction (optional)
    - IssuingBody (optional)
    - Title (optional)
    - Content (optional)

```sql
EXEC search_legislation 
	@Jurisdiction = 'Japan', 
    @Content = 'Enforcement'
```

2. **search_any**: Searches legislation for a substring in the follow fields: legislation title, jurisdiction name, issuing body name, parts content.
    - Search

```sql
EXEC search_any 
	@Search = 'tax', 
```
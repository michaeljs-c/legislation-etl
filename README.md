# Legislation ETL
ETL application processing legislation data and deployed on Azure.


## Directory structure
1. legislation_files - contains json files with legislation data
2. local - docker files for building and running local dockerised app
3. trigger_etl - core functionality
    - azure_etl.py - Azure app entry point
    - etl.py - core functionality for both azure and local deployment

## Data Models
1. legislation: basis of a real-world legal document that contains rules and regulations.
2. Legislation version: a specific version of a piece of legislation.
3. Issuing body: the organization responsible for creating and issuing the legislation.
4. Jurisdiction: the geographic area where a particular set of laws and regulations applies.
5. Parts: the various components of legislation that organize and structure the document into sections, chapters, paragraphs, and clauses.

## Running the application locally

Bringing up SQL Server:
```sh
cd local
docker-compose up
```
Building the app image:
```
docker build -f local/Dockerfile -t cube-etl .
```
The image was developed on a linux machine, no guarentee that the odbc setup script will work on Windows, if any issues:
- Replace the setup_odbc.sh file with suitable odbc setup script (and change Dockerfile line: `RUN bash -c "./setup_odbc.sh"`), or,
- Call the CLI directly with python instead (see below)

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
The API can either be called via a web browser or via API request as demonstrated below.

To Run the ETL (FYI this takes ~5 minutes, expect this much time before receiving a http response):
```py
import requests

url = "https://cube-etl.azurewebsites.net/api/trigger_etl?function=etl"
response = requests.get(url)
print(response.content)

```
To drop the database (~10 seconds):

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
	@Search = 'tax'
```

## Next Steps
1. Unit and integration testing
2. Move db credentials to env variables (create config files for other hard coded vars)
2. Event trigger for ETL when new files placed in blob bucket
    - Possibly move processed files into different bucket
3. Data validation for input json files
4. Power BI dashboard for insights
5. Look for any inefficiencies (container/azurefunc memory, query performance etc)

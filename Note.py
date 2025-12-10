#uvx pycowsay 'FastAPI'
#> celery -A src.celery_tasks.c_app worker --loglevel=info --pool=solo
#> celery -A src.celery_tasks.c_app flower --port=5555 --address=127.0.0.1
#> http://127.0.0.1:5555/
#? model_dump() and model_validate()

#! model_dump() is used to convert  pydantic object -> normal python Dict
#! model_validate() is used to convert normal python Dict -> pydantic object
#> +-----------------+---------------------------------------------+-------------------------------+---------------------------------------------------------------+
#> | Function        | Input                                       | Output                        | Primary Goal                                                  |
#> +-----------------+---------------------------------------------+-------------------------------+---------------------------------------------------------------+
#> | model_validate()| Unchecked/Raw Data (e.g., dict, JSON)       | Validated Pydantic Instance   | Data Integrity: Ensures the raw input follows model rules     |
#> | model_dump()    | Pydantic Instance                           | Standard Python dict          | Serialization: Prepare data for storage or returning as JSON  |
#> +-----------------+---------------------------------------------+-------------------------------+---------------------------------------------------------------+

## model_dump() Parameters (Converting Model -> Dict)
#> +-------------------+------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
#> | Parameter         | Type                   | Default | Concise Purpose                                                                                                                  |
#> +-------------------+------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
#> | mode              | 'json' or 'python'     | 'json'  | Controls format: 'json' serializes data (e.g., datetime→ISO string); 'python' keeps native Python types.                         |
#> | exclude_unset     | bool                   | False   | Exclude optional fields: If True, fields not explicitly set by the user (even if they have defaults) are omitted.                |
#> | by_alias          | bool                   | False   | Use JSON aliases: If True, output dict keys use alias names defined in the model.                                                |
#> | include / exclude | Set[str]               | None    | Filter fields: Explicitly specify which fields to include or exclude in the output dictionary.                                   |
#> +-------------------+------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+

## model_validate() Parameters (Converting Dict -> Model)
#> +------------------+-----------+---------+------------------------------------------------------------------------------------------------------------------------------------+
#> | Parameter        | Type      | Default | Concise Purpose                                                                                                                    |
#> +------------------+-----------+---------+------------------------------------------------------------------------------------------------------------------------------------+
#> | strict           | bool      | None    | Disable type coercion: If True, Pydantic will NOT convert types (e.g., "123" → int fails).                                         |
#> | context          | dict      | None    | Pass extra data: Provides a dict of values accessible inside custom validators for conditional logic.                              |
#> | from_attributes  | bool      | False   | Validate from objects: Allows reading values from object attributes (e.g., ORM objects), not only dictionary keys.                 |
#> +------------------+-----------+---------+------------------------------------------------------------------------------------------------------------------------------------+

#!   alembic commands
## uv run alembic init -t async migrations
#! to commit migrations
## uv run alembic --config src/alembic.ini revision --autogenerate -m "Initial migration"
#! to apply migrations
## uv run alembic --config src/alembic.ini upgrade head
#! to rollback last migration
## uv run alembic --config src/alembic.ini downgrade -1
#> +------------------------+-----------------------------------------------+-----------------------------------------------+
#> | MIGRATION STEP         | COMMAND                                       | DESCRIPTION                                   |
#> +------------------------+-----------------------------------------------+-----------------------------------------------+
#> | Install Alembic        | uv add alembic                                | Add Alembic to your FastAPI project.          |
#> +------------------------+-----------------------------------------------+-----------------------------------------------+
#> | Initialize Alembic     | alembic init migrations                        | Creates migrations folder + config files.    |
#> +------------------------+-----------------------------------------------+-----------------------------------------------+
#> | Set DB URL             | edit alembic.ini                              | Add your database connection string.          |
#> +------------------------+-----------------------------------------------+-----------------------------------------------+
#> | Link Models Metadata   | edit migrations/env.py                        | Import Base/SQLModel metadata for Alembic.    |
#> +------------------------+-----------------------------------------------+-----------------------------------------------+
#> | Autogenerate Migration | alembic revision --autogenerate -m "message"  | Creates migration based on model changes.     |
#> +------------------------+-----------------------------------------------+-----------------------------------------------+
#> | Apply Migration        | alembic upgrade head                          | Updates DB schema to the latest version.      |
#> +------------------------+-----------------------------------------------+-----------------------------------------------+
#> | Rollback Migration     | alembic downgrade -1                          | Undo the most recent migration.               |
#> +------------------------+-----------------------------------------------+-----------------------------------------------+
#> | View History           | alembic history                               | Shows previous and pending migrations.        |
#> +------------------------+-----------------------------------------------+-----------------------------------------------+
#> | Stamp DB State         | alembic stamp head                            | Mark the DB as up-to-date without running.    |
#> +------------------------+-----------------------------------------------+-----------------------------------------------+
#> | Manual Revision        | alembic revision -m "message"                 | Creates an empty migration file manually.     |
#> +------------------------+-----------------------------------------------+-----------------------------------------------+

#! JWT secret key in .env file
import secrets
print(secrets.token_hex(16))



#!-------------- Role Based Access Control (RBAC) --------------!#
## admin 
[
    "adding users",
    "change user roles",
    "crud on users",
    'book submissions',
    "crud on reviews",
    "revoking access tokens",
]

##  users
[
    "crud on their own book submissions",
    "crud on their own reviews",
    "crud on their own accounts",
]

#! Dependencies Types: 
#> 1) Function Dependency
#> 2) Class Dependency
#> 3) Sub-dependencies




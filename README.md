# FastAPI & PostgreSQL

- FastAPI with psycopg (async)
- FastAPI with asyncpg (async)
- FastAPI with SQLAlchemy (async)

Automatic commits & rollbacks using FastAPI's dependency injection system.

Interesting comparison between psycopg & asyncpg: https://fernandoarteaga.dev/blog/psycopg-vs-asyncpg/

## Getting started

- [Run PostgreSQL in a docker container](https://medium.com/@okpo65/mastering-postgresql-with-docker-a-step-by-step-tutorial-caef03ab6ae9):

```bash
make start-db
```

- Create the tables by executing the SQL statements in [db/schema.sql](db/schema.sql).

### FastAPI with psycopg

Go to [app_psycopg](src/app_psycopg)

### FastAPI with SQLAlchemy (async)

Go to [app_sqlalchemy](src/app_sqlalchemy)

Based on https://chaoticengineer.hashnode.dev/fastapi-sqlalchemy

Other resources:

- https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308
- https://medium.com/@navinsharma9376319931/mastering-fastapi-crud-operations-with-async-sqlalchemy-and-postgresql-3189a28d06a2
- https://github.com/ThomasAitken/demo-fastapi-async-sqlalchemy/tree/main

### FastAPI with asyncpg

Go to [app_asyncpg](src/app_asyncpg)

## TODO

- [ ] Create erd diagram
- [ ] SQLAlchemy app
- [ ] Add filters, sorting
- [ ] Automatic commit/Rollback

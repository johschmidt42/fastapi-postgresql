# To do stuff with make, you type `make` in a directory that has a file called
# "Makefile". You can also type `make -f <makefile>` to use a different filename.
#
# A Makefile is a collection of rules. Each rule is a recipe to do a specific
# thing, sort of like a grunt task or an npm package.json script.
#
# A rule looks like this:
#
# <target>: <prerequisites...>
# 	<commands>
#
# The "target" is required. The prerequisites are optional, and the commands
# are also optional, but you have to have one or the other.
#
# Type `make` to show the available targets and a description of each.
#
.DEFAULT_GOAL := help
.PHONY: help
help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

DATABASE = "postgres"
MOUNT = "../postgresql-mount"
POSTGRES_USER = "admin"
POSTGRES_PASSWORD = "admin"

##@ Run

start-db:  ## starts postgreSQL with docker
	mkdir -p $(MOUNT)
	docker run --name my-postgres -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) -e POSTGRES_DB=$(DATABASE) -v ./$(MOUNT):/var/lib/postgresql/data -p 5432:5432 --rm postgres:latest

start-db-compose:  ## same as the 'start-db' command but with docker-compose
	mkdir -p $(MOUNT)
	docker-compose up

##@ Formatting

format:  ## format code using ruff
	@ruff format .
	@ruff check --fix-only .

##@ Linting

lint-py:  ## run linter using ruff
	@ruff format . --check
	@ruff check .

.PHONY: lint-sql
lint-sql: ## sqlfluff (sql linter)
	@sqlfluff lint db/* --dialect postgres

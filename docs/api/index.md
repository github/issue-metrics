# API

some facts about stuff


# Running the service
The [CLI](../cli/index) has a build-in commands to help bootstrap and start the service.

Before being able to run the service with the cli we must first start its dependencies and configure them. This requires
docker compose to be run. The docker compose file can be found here: `infrastructure/images/docker-compose.yaml`. There
are some additional services can be removed if not interested in using them.

```{note}
:class: note

This should all be running in k8s locally.  However, I ran out of time.
```

```shell
docker compose  --project-directory ./infrastructure/images up
```

After all containers are running there are a few steps to prepare the database. These commands are part of the
[CLI](../cli/index).

These commands will create a keyspace, tables, and insert some data into the tables.

```shell
poetry run python-template db keyspaces create nerds
poetry run python-template db tables -k nerds create
poetry run python-template db tables -k nerds insert
```

```shell
poetry run python-template start
```

This will start the service along with a watchdog process looking for changes. In addition, the service has two
documentation endpoints and a status endpoint for health checks. Both redoc and open api provide the same functionality
they just have a different look and feel. After the service is running verify that it has some data in the service get
http request using one of the documentation tools linked below.

The response should look like the following.
```json
{
  "data": [
    {
      "environments": [
        "performance-dev"
      ],
      "service_id": "2f31fd25-1eac-40f2-8a2a-72f24c0de567",
      "service_name": "mongodb",
      "service_description": "MongoDB its web scale!",
      "tags": [
        "dev",
        "performance",
        "aws"
      ]
    }
  ],
  "metadata": {
    "limit": 25,
    "offset": 0,
    "response_time": 0.000007,
    "status_code": 200,
    "total_results": 0
  },
  "notifications": {
    "info": [],
    "warning": [],
    "error": []
  }
}
```

## Important Endpoints

```{attention}
:class: attention

The following links assume the application is running locally.
```

[Status Endpoint](http://localhost:5000/v1/status)
: This endpoint is intended to show the status of dependent services and other health related metadata.

[Redoc Endpoint](http://localhost:5000/redoc)
: This endpoint shows the services routes responses and requests.

[OpenAPI Endpoint](http://localhost:5000/docs)
: This endpoint shows the services routes responses and requests.


```{toctree}
:hidden:

```

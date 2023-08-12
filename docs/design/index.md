# Design

Please keep in mind that this project is not complete and likely still has months of development time to get to an MVP
state. Do not be surprised if you find a lot of half implemented functionality.

The project design is intended to be self-contained and include up to four major components an API, SDK, Daemon, and CLI.

The API, a restful service. This is where most if not all application business logic should live. The service uses plurals for
resource names `/dogs` not `/dog`. In addition, the routes are prefixed with the API version `/v1/resource`. For metrics
there is a prometheus endpoint at `/v1/metrics`. Health checks should be pointed at `/v1/status`. OpenAPI spec is also
implemented and can be found at `/docs` or `/redocs`.  The database is [Scylla](https://docs.scylladb.com/stable/) which
has two query language choices cassandra sql or dynamoDB.

The SDK, a python package that uses the same response and requests schemas as the API and provides an interface
to the service. There is also the beginnings of a plugin framework in place. This should be used for any external service
integrations. Some examples, AWS, OpsManager, and MongoDB. Generally speaking most things should be proxied threw the
API unless it makes sense to expose the interface directly to end users or the CLI.

The CLI, a command line tool that uses the SDK to interact with API to do tasks/actions/CRUD. There are also a
collection of helper commands for development and reporting.  As a rule of thumb most commands should be direct API
calls. However, with reporting and one off tasks might directly interact with plugins. (most of the
functionality of the application is only available using the CLI)

The Daemon isn't required, however, would provide value, an example use case for adding a daemon would be monitoring
active times and time to retire times. The daemon would pull on an interval and take action if the service has met its
retirement time or start a service based on active times. Like the CLI the Daemon should be using the SDK and primarily
making requests to the API. The Daemon core logic is mostly complete. some facts about stuff

```{toctree}
:hidden:

structure
workflow
```

[Workflow](./workflow)
: Describes the various workflows for this project.

[Structure](./structure)
: Describes how the project layout and how the various parts of it work.

# PyPaperless

![Test Badge](https://github.com/tb1337/paperless-api/actions/workflows/test.yml/badge.svg) [![codecov](https://codecov.io/gh/tb1337/paperless-api/graph/badge.svg?token=IMXRBK3HRE)](https://codecov.io/gh/tb1337/paperless-api)

Little api client for [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx)!

Find out more here:

* Project: https://docs.paperless-ngx.com
* REST API: https://docs.paperless-ngx.com/api/

## Features

- Depends on aiohttp, works in async environments.
- Token authentication only. **No credentials anymore.**
- `list()` requests all object ids of resources.
- `get()` for each resources. Accepts Django filters.
- `iterate()` for each endpoint. Accepts Django filters.
- `create()`, `update()`, `delete()` methods for many resources.
- Paperless makes use of pagination. We use that too. You have full control.
- *PyPaperless* only transports data. Your code organizes it.

## Documentation

* [Handling a session](docs/SESSION.md)
* [Request data](docs/REQUEST.md)
* [Create, update, delete data](docs/CRUD.md)

## Thanks to

* The Paperless-ngx Team
* The Home Assistant Community

# PyPaperless

[![GitHub Release][release-badge]][release-url]
[![Python Version][python-badge]][python-url]
[![GitHub License][license-badge]][license-url]

[![Tests][tests-badge]][tests-url]
[![Codecov][codecov-badge]][codecov-url]
[![Linting][linting-badge]][linting-url]
[![Typing][typing-badge]][typing-url]

Little asynchronous client for Paperless-ngx, written in Python. You should at least use Python `>=3.12`.

**v4 upgrade warning**

* We dropped support for Python `<=3.11`.
* Major changes in various classes occurred. Consider using Paperless-ngx `>=2.15.0`.
* Support for Paperless-ngx `<2.15.0` will end after 2025/07.

## Features

- Depends on aiohttp, works in async environments.
- Token authentication only. **No credentials anymore.**
- Request single resource items.
- Iterate over all resource items or request them page by page.
- Create, update and delete resource items.
- Almost feature complete.
- _PyPaperless_ is designed to transport data only. Your code must organize it.

Find out more about Paperless-ngx here:

- Project: https://docs.paperless-ngx.com
- API Docs: https://docs.paperless-ngx.com/api/
- Source Code: https://github.com/paperless-ngx/paperless-ngx

## Installation

```bash
pip install pypaperless
```

## Documentation

Please check out the **[docs][docs-url]** for detailed instructions and examples.

## Authors & contributors

_PyPaperless_ is written by [Tobias Schulz][contributors-tbsch]. Its his first Python project. Feedback appreciated.

Check out all [contributors here][contributors-url].

[codecov-badge]: https://codecov.io/gh/tb1337/paperless-api/graph/badge.svg?token=IMXRBK3HRE
[codecov-url]: https://app.codecov.io/gh/tb1337/paperless-api/tree/main
[contributors-tbsch]: https://tbsch.de
[contributors-url]: https://github.com/tb1337/paperless-api/graphs/contributors
[docs-url]: https://github.com/tb1337/paperless-api/blob/main/docs/usage.md
[license-badge]: https://img.shields.io/github/license/tb1337/paperless-api
[license-url]: /LICENSE.md
[python-badge]: https://img.shields.io/pypi/pyversions/pypaperless
[python-url]: https://pypi.org/project/pypaperless/
[tests-badge]: https://github.com/tb1337/paperless-api/actions/workflows/tests.yml/badge.svg
[tests-url]: https://github.com/tb1337/paperless-api/actions
[release-badge]: https://img.shields.io/github/v/release/tb1337/paperless-api
[release-url]: https://github.com/tb1337/paperless-api/releases
[linting-badge]: https://github.com/tb1337/paperless-api/actions/workflows/linting.yml/badge.svg
[linting-url]: https://github.com/tb1337/paperless-api/actions
[typing-badge]: https://github.com/tb1337/paperless-api/actions/workflows/typing.yml/badge.svg
[typing-url]: https://github.com/tb1337/paperless-api/actions

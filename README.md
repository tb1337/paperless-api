# PyPaperless

[![GitHub Release][release-badge]][release-url]
[![Python Version][python-badge]][python-url]
[![GitHub License][license-badge]][license-url]

[![Tests][tests-badge]][tests-url]
[![Codecov][codecov-badge]][codecov-url]
[![Typing and Linting][typing-linting-badge]][typing-linting-url]

Little asynchronous client for Paperless-ngx, written in Python. You should at least use Python `>=3.11`.

Find out more about Paperless-ngx here:

- Project: https://docs.paperless-ngx.com
- API Docs: https://docs.paperless-ngx.com/api/
- Source Code: https://github.com/paperless-ngx/paperless-ngx

## Features

- Depends on aiohttp, works in async environments.
- Token authentication only. **No credentials anymore.**
- Request single resource items.
- Iterate over all resource items or request them page by page.
- Create, update and delete resource items.
- Almost feature complete.
- _PyPaperless_ is designed to transport data only. Your code must organize it.

## Installation

```bash
pip install pypaperless
```

## Documentation

Please check out the **[docs][docs-url]** for detailed instructions and examples.

## Authors & contributors

_PyPaperless_ is written by [Tobias Schulz][contributors-tbsch]. Its his first Python project. Feedback appreciated.

Check out all [contributors here][contributors-url].

## Thanks to

- The Paperless-ngx Team
- The Home Assistant Community

[codecov-badge]: https://codecov.io/gh/tb1337/paperless-api/graph/badge.svg?token=IMXRBK3HRE
[codecov-url]: https://app.codecov.io/gh/tb1337/paperless-api/tree/main
[contributors-tbsch]: https://tbsch.de
[contributors-url]: https://github.com/tb1337/paperless-api/graphs/contributors
[docs-url]: /docs/usage.md
[license-badge]: https://img.shields.io/github/license/tb1337/paperless-api
[license-url]: /LICENSE.md
[python-badge]: https://img.shields.io/pypi/pyversions/pypaperless
[python-url]: https://pypi.org/project/pypaperless/
[tests-badge]: https://github.com/tb1337/paperless-api/actions/workflows/tests.yml/badge.svg
[tests-url]: https://github.com/tb1337/paperless-api/actions
[release-badge]: https://img.shields.io/github/v/release/tb1337/paperless-api
[release-url]: https://github.com/tb1337/paperless-api/releases
[typing-linting-badge]: https://github.com/tb1337/paperless-api/actions/workflows/typing-linting.yml/badge.svg
[typing-linting-url]: https://github.com/tb1337/paperless-api/actions

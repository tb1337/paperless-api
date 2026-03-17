"""PyPaperless CLI."""

import asyncio
import json
import sys
from collections.abc import Awaitable, Callable
from typing import Any

import click

try:
    from pygments import highlight
    from pygments.formatters import TerminalFormatter
    from pygments.lexers import JsonLexer

    _PYGMENTS = True
except ImportError:
    _PYGMENTS = False

from . import Paperless
from .const import ENV_TOKEN, ENV_URL
from .exceptions import (
    ForbiddenError,
    InitializationError,
    InvalidTokenError,
    PaperlessConnectionError,
)


def _out(obj: Any) -> None:
    """Dump *obj* as indented JSON to stdout, with syntax highlighting when connected to a TTY."""
    text = json.dumps(obj, indent=2, default=str)
    if sys.stdout.isatty() and _PYGMENTS:
        text = highlight(text, JsonLexer(), TerminalFormatter())
    click.echo(text)


def _render_compact_list(items: list[Any]) -> None:
    """Render a compact ID/Name listing from model instances."""
    rows: list[tuple[str, str]] = []
    for item in items:
        item_id = str(getattr(item, "id", "") or "")
        row_name = ""
        for key in ("name", "title", "username", "task_id", "slug"):
            value = getattr(item, key, None)
            if value not in (None, ""):
                row_name = str(value)
                break
        rows.append((item_id, row_name))

    rows.sort(key=lambda row: (row[1].casefold(), row[0]))
    id_width = max((len(row[0]) for row in rows), default=2)
    click.echo(f"{'ID':<{id_width}}  Name")
    click.echo(f"{'-' * id_width}  {'-' * 40}")
    for row_id, row_name in rows:
        click.echo(f"{row_id:<{id_width}}  {row_name}")


async def _with_client(
    url: str | None,
    token: str | None,
    coro: Callable[[Paperless], Awaitable[None]],
) -> None:
    """Build a ``Paperless`` client, initialize it, run ``coro(paperless)``, then close."""
    if url is not None:
        paperless = Paperless(url=url, token=token)
    else:
        try:
            paperless = Paperless()
        except Exception as exc:
            msg = f"Configuration error: {exc}"
            raise click.ClickException(msg) from exc

    try:
        async with paperless:
            await coro(paperless)
    except PaperlessConnectionError as exc:
        msg = f"Connection error: {exc}"
        raise click.ClickException(msg) from exc
    except InvalidTokenError as exc:
        msg = "Authentication failed — invalid or missing token."
        raise click.ClickException(msg) from exc
    except ForbiddenError as exc:
        msg = "Access denied (HTTP 403)."
        raise click.ClickException(msg) from exc
    except InitializationError as exc:
        msg = f"Initialization failed: {exc}"
        raise click.ClickException(msg) from exc


@click.group()
@click.option(
    "--url",
    envvar=ENV_URL,
    default=None,
    metavar="URL",
    help=f"Paperless-ngx base URL  [env: {ENV_URL}]",
)
@click.option(
    "--token",
    envvar=ENV_TOKEN,
    default=None,
    metavar="TOKEN",
    help=f"API token  [env: {ENV_TOKEN}]",
)
@click.pass_context
def cli(ctx: click.Context, url: str | None, token: str | None) -> None:
    r"""PyPaperless — command-line interface for Paperless-ngx.

    \b
    Credentials can be supplied as options or via environment variables:
      PYPAPERLESS_URL    base URL of your Paperless-ngx instance
      PYPAPERLESS_TOKEN  API token
    """
    ctx.ensure_object(dict)
    ctx.obj["url"] = url
    ctx.obj["token"] = token


@cli.command("status")
@click.pass_context
def cmd_status(ctx: click.Context) -> None:
    """Show host version, API version and system status."""

    async def _fetch(p: Paperless) -> None:
        stat = await p.status()
        rv = await p.remote_version()
        _out(
            {
                "host_version": p.host_version,
                "api_version": p.host_api_version,
                "status": stat.model_dump(mode="json"),
                "remote_version": rv.model_dump(mode="json"),
            }
        )

    asyncio.run(_with_client(ctx.obj["url"], ctx.obj["token"], _fetch))


@cli.command("profile")
@click.pass_context
def cmd_profile(ctx: click.Context) -> None:
    """Show the currently authenticated user's profile."""

    async def _fetch(p: Paperless) -> None:
        item = await p.profile()
        _out(item.model_dump(mode="json"))

    asyncio.run(_with_client(ctx.obj["url"], ctx.obj["token"], _fetch))


def _resource_group(
    name: str,
    service_attr: str,
    *,
    supports_get: bool = True,
    supports_list: bool = True,
    id_type: click.ParamType = click.INT,
) -> click.Group:
    """Return a ``click.Group`` with ``list`` and/or ``get`` subcommands.

    `name`: CLI group name (e.g. ``"tags"``).
    `service_attr`: attribute on the ``Paperless`` instance (e.g. ``"tags"``).
    `supports_get`: add a ``get <id>`` subcommand.
    `supports_list`: add a ``list`` subcommand.
    `id_type`: click parameter type for the ``get`` argument (default: ``INT``).
    """

    @click.group(name)
    def grp() -> None:
        pass

    if supports_list:

        @grp.command("list")
        @click.option(
            "--limit",
            default=None,
            type=int,
            metavar="N",
            help="Stop after N items (default: all).",
        )
        @click.pass_context
        def list_cmd(ctx: click.Context, limit: int | None) -> None:
            """List item IDs and names in a compact console format."""
            _attr = service_attr

            async def _fetch(p: Paperless) -> None:
                service = getattr(p, _attr)
                results: list[Any] = []
                count = 0
                async for item in service:
                    results.append(item)
                    count += 1
                    if limit is not None and count >= limit:
                        break
                _render_compact_list(results)

            asyncio.run(_with_client(ctx.obj["url"], ctx.obj["token"], _fetch))

        @grp.command("json")
        @click.option(
            "--limit",
            default=None,
            type=int,
            metavar="N",
            help="Stop after N items (default: all).",
        )
        @click.pass_context
        def json_cmd(ctx: click.Context, limit: int | None) -> None:
            """List full items as JSON objects."""
            _attr = service_attr

            async def _fetch(p: Paperless) -> None:
                service = getattr(p, _attr)
                results: list[dict[str, Any]] = []
                count = 0
                async for item in service:
                    results.append(item.model_dump(mode="json"))
                    count += 1
                    if limit is not None and count >= limit:
                        break
                _out(results)

            asyncio.run(_with_client(ctx.obj["url"], ctx.obj["token"], _fetch))

    if supports_get:

        @grp.command("get")
        @click.argument("item_id", type=id_type, metavar="ID")
        @click.pass_context
        def get_cmd(ctx: click.Context, item_id: Any) -> None:
            """Fetch a single item by ID."""
            _attr = service_attr

            async def _fetch(p: Paperless) -> None:
                service = getattr(p, _attr)
                item = await service(item_id)
                _out(item.model_dump(mode="json"))

            asyncio.run(_with_client(ctx.obj["url"], ctx.obj["token"], _fetch))

    return grp


cli.add_command(_resource_group("correspondents", "correspondents"))
cli.add_command(_resource_group("custom-fields", "custom_fields"))
cli.add_command(_resource_group("document-types", "document_types"))
cli.add_command(_resource_group("documents", "documents"))
cli.add_command(_resource_group("groups", "groups"))
cli.add_command(_resource_group("mail-accounts", "mail_accounts"))
cli.add_command(_resource_group("mail-rules", "mail_rules"))
cli.add_command(_resource_group("saved-views", "saved_views"))
cli.add_command(_resource_group("share-links", "share_links"))
cli.add_command(_resource_group("storage-paths", "storage_paths"))
cli.add_command(_resource_group("tags", "tags"))
cli.add_command(_resource_group("tasks", "tasks", id_type=click.STRING))
cli.add_command(_resource_group("trash", "trash", supports_get=False))
cli.add_command(_resource_group("users", "users"))
cli.add_command(_resource_group("workflows", "workflows"))

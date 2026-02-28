"""CLI entry point for mkwineprefix."""

from __future__ import annotations

from pathlib import Path
from shlex import quote
from typing import get_args
import subprocess as sp
import sys

from bascom import setup_logging
import click

from .prefix import DEFAULT_DPI, WineWindowsVersion, create_wine_prefix


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.argument('prefix_name')
@click.option('-D', '--dpi', default=DEFAULT_DPI, type=int, help='DPI.')
@click.option('-d', '--debug', is_flag=True, help='Enable debug output.')
@click.option('--disable-explorer',
              is_flag=True,
              help='Disable starting explorer.exe automatically.')
@click.option(
    '--disable-services',
    is_flag=True,
    help=('Disable starting services.exe automatically (only useful for simple CLI '
          'programs with --disable-explorer).'),
)
@click.option('-E', '--eax', is_flag=True, help='Enable EAX.')
@click.option('-g', '--gtk', is_flag=True, help='Enable Gtk+ theming.')
@click.option('-r', '--prefix-root', type=click.Path(path_type=Path), help='Prefix root.')
@click.option('-S', '--sandbox', is_flag=True, help='Sandbox the prefix.')
@click.option('--no-gecko', is_flag=True, help='Disable downloading Gecko automatically.')
@click.option('--no-mono', is_flag=True, help='Disable downloading Mono automatically.')
@click.option('--no-xdg', is_flag=True, help='Disable winemenubuilder.exe.')
@click.option(
    '--no-assocs',
    is_flag=True,
    help=('Disable creating file associations, but still allow menu entries to be made'
          ' (unless --no-xdg is also passed).'),
)
@click.option('-N', '--nvapi', help='Add dxvk-nvapi.', is_flag=True)
@click.option('-o', '--noto', is_flag=True, help='Use Noto Sans in place of most fonts.')
@click.option('-T', '--trick', 'tricks', help='Add an argument for winetricks.', multiple=True)
@click.option('-t', '--tmpfs', is_flag=True, help='Make Wine use tmpfs.')
@click.option(
    '-V',
    '--windows-version',
    default='10',
    type=click.Choice(get_args(WineWindowsVersion)),
    help='Windows version.',
)
@click.option('--vd',
              metavar='SIZE',
              nargs=1,
              default='off',
              help='Virtual desktop size, e.g. 1024x768.')
@click.option('-W', '--winrt-dark', is_flag=True, help='Enable dark mode for WinRT apps.')
@click.option('-x', '--dxva-vaapi', is_flag=True, help='Enable DXVA2 support with VA-API.')
@click.option('--32', '_32bit', help='Use 32-bit prefix.', is_flag=True)
def main(
    prefix_name: str,
    prefix_root: Path | None,
    tricks: tuple[str, ...],
    vd: str = 'off',
    windows_version: WineWindowsVersion = '10',
    *,
    _32bit: bool = False,
    asio: bool = False,
    debug: bool = False,
    disable_explorer: bool = False,
    disable_services: bool = False,
    dpi: int = DEFAULT_DPI,
    dxva_vaapi: bool = False,
    eax: bool = False,
    gtk: bool = False,
    no_assocs: bool = False,
    no_gecko: bool = False,
    no_mono: bool = False,
    no_xdg: bool = False,
    noto: bool = False,
    nvapi: bool = False,
    sandbox: bool = False,
    tmpfs: bool = False,
    winrt_dark: bool = False,
) -> None:
    """
    Create a Wine prefix with custom settings.

    This should be used with eval: eval $(mkwineprefix ...)
    """  # noqa: DOC501
    setup_logging(debug=debug, loggers={'mkwineprefix': {}})
    try:
        target = create_wine_prefix(
            prefix_name,
            _32bit=_32bit,
            asio=asio,
            disable_explorer=disable_explorer,
            disable_services=disable_services,
            dpi=dpi,
            dxva_vaapi=dxva_vaapi,
            dxvk_nvapi=nvapi,
            eax=eax,
            gtk=gtk,
            no_associations=no_assocs,
            no_gecko=no_gecko,
            no_mono=no_mono,
            no_xdg=no_xdg,
            noto_sans=noto,
            prefix_root=prefix_root,
            sandbox=sandbox,
            tmpfs=tmpfs,
            tricks=tricks,
            vd=vd,
            windows_version=windows_version,
            winrt_dark=winrt_dark,
        )
    except FileExistsError as e:
        raise click.Abort from e
    except sp.CalledProcessError as e:
        click.echo(f'Exception: {e}', err=True)
        click.echo(f'STDERR: {e.stderr}', err=True)
        click.echo(f'STDOUT: {e.stdout}', err=True)
        raise click.Abort from e
    wineprefix_env = quote(f'WINEPREFIX={target}')
    click.echo(
        f"""Run `export WINEPREFIX={target}` before running wine or use env:

env {wineprefix_env} wine ...

If you ran this with eval, your shell is ready.""",
        file=sys.stderr,
    )
    click.echo(f'export {wineprefix_env}')
    click.echo(f'export PS1="{prefix_name}🍷$PS1"')

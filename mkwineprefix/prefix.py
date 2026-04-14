"""Create a Wine prefix with custom settings."""
# ruff: noqa: N815

from __future__ import annotations

from functools import partial
from io import BytesIO
from os import PathLike, environ
from pathlib import Path
from shlex import quote
from shutil import copyfile, rmtree, which
from typing import TYPE_CHECKING, Any, Literal, NamedTuple, TypeAlias
import asyncio
import logging
import sqlite3
import struct
import subprocess as sp
import tarfile
import tempfile

from anyio import Path as AsyncPath
from anyio.to_thread import run_sync as run_in_thread
import niquests
import platformdirs
import xz

from ._windows import (
    LF_FULLFACESIZE,
    CharacterSet,
    ClipPrecision,
    Family,
    OutputPrecision,
    Pitch,
    Quality,
    Weight,
)

if TYPE_CHECKING:
    from collections.abc import Coroutine, Iterable

__all__ = ('create_wine_prefix',)

StrPath: TypeAlias = str | PathLike[str]
log = logging.getLogger(__name__)


async def _run_reg(env: dict[str, str], *args: str, wine_bin: str = 'wine') -> None:
    cmd = (wine_bin, 'reg', 'add', *args)
    log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
    proc = await asyncio.create_subprocess_exec(*cmd, env=env)
    returncode = await proc.wait()
    if returncode:
        raise sp.CalledProcessError(returncode, cmd[0])


async def _run_cmd(cmd: tuple[str, ...], env: dict[str, str] | None = None) -> None:
    log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
    proc = await asyncio.create_subprocess_exec(*cmd, env=env)
    returncode = await proc.wait()
    if returncode:
        raise sp.CalledProcessError(returncode, cmd[0])


WineWindowsVersion = Literal['11', '10', 'vista', '2k3', '7', '8', 'xp', '81', '2k', '98', '95']
"""Windows versions supported by Wine."""
DEFAULT_DPI = 96
"""Default DPI for Wine prefixes."""

WINETRICKS_VERSION_MAPPING = {
    '11': 'win11',
    '10': 'win10',
    'vista': 'vista',
    '2k3': 'win2k3',
    '7': 'win7',
    '8': 'win8',
    'xp': 'winxp',
    '81': 'win81',
    '2k': 'win2k',
    '98': 'win98',
    '95': 'win95',
}
_CREATE_WINE_PREFIX_NOTO_FONT_REPLACEMENTS = {
    'Arial Baltic,186',
    'Arial CE,238',
    'Arial CYR,204',
    'Arial Greek,161',
    'Arial TUR,162',
    'Courier New Baltic,186',
    'Courier New CE,238',
    'Courier New CYR,204',
    'Courier New Greek,161',
    'Courier New TUR,162',
    'Helv',
    'Helvetica',
    'MS Shell Dlg',
    'MS Shell Dlg 2',
    'MS Sans Serif',
    'Segoe UI',
    'System',
    'Tahoma',
    'Times',
    'Times New Roman Baltic,186',
    'Times New Roman CE,238',
    'Times New Roman CYR,204',
    'Times New Roman Greek,161',
    'Times New Roman TUR,162',
    'Tms Rmn',
    'Verdana',
}
_CREATE_WINE_PREFIX_NOTO_REGISTRY_ENTRIES = {
    'Caption',
    'Icon',
    'Menu',
    'Message',
    'SmCaption',
    'Status',
}


class LOGFONTW(NamedTuple):
    """Windows LOGFONTW structure as a named tuple."""

    lfHeight: int
    lfWidth: int
    lfEscapement: int
    lfOrientation: int
    lfWeight: int
    lfItalic: bool
    lfUnderline: bool
    lfStrikeOut: bool
    lfCharSet: int
    lfOutPrecision: int
    lfClipPrecision: int
    lfQuality: int
    lfPitchAndFamily: int


Q4WINE_DEFAULT_ICONS: tuple[tuple[str, str, str, str, str, str], ...] = (
    ('', 'control.exe', 'control', 'Wine control panel', 'system', 'Control Panel'),
    ('', 'eject.exe', 'eject', 'Wine CD eject tool', 'system', 'Eject'),
    (
        '',
        'explorer.exe',
        'explorer',
        'Browse the files in the virtual Wine Drive',
        'system',
        'Explorer',
    ),
    ('', 'iexplore.exe', 'iexplore', 'Wine internet browser', 'system', 'Internet Explorer'),
    ('', 'notepad.exe', 'notepad', 'Wine notepad text editor', 'system', 'Notepad'),
    ('', 'oleview.exe', 'oleview', 'Wine OLE/COM object viewer', 'system', 'OLE Viewer'),
    ('', 'regedit.exe', 'regedit', 'Wine registry editor', 'system', 'Registry Editor'),
    ('', 'taskmgr.exe', 'taskmgr', 'Wine task manager', 'system', 'Task Manager'),
    (
        '',
        'uninstaller.exe',
        'uninstaller',
        'Uninstall Windows programs under Wine properly',
        'system',
        'Uninstaller',
    ),
    (
        '',
        'winecfg.exe',
        'winecfg',
        'Configure the general settings for Wine',
        'system',
        'Configuration',
    ),
    (
        '',
        'wineconsole',
        'wineconsole',
        'Wineconsole is similar to wine command wcmd',
        'system',
        'Console',
    ),
    ('', 'winemine.exe', 'winemine', 'Wine sweeper game', 'system', 'Winemine'),
    ('', 'wordpad.exe', 'wordpad', 'Wine wordpad text editor', 'system', 'WordPad'),
)


def _build_prefix_env(target: Path, *, _32bit: bool = False) -> dict[str, str]:
    arch = 'win32' if _32bit else None
    esync = environ.get('WINEESYNC', '')
    env = {
        'DISPLAY': environ.get('DISPLAY', ''),
        'PATH': environ['PATH'],
        'WINEPREFIX': str(target),
        'XAUTHORITY': environ.get('XAUTHORITY', ''),
        'WINEDEBUG': environ.get('WINEDEBUG', 'fixme-all'),
    }
    if arch:
        env['WINEARCH'] = environ.get('WINEARCH', arch)
    if esync:  # pragma: no cover
        env['WINEESYNC'] = esync
    return env


async def _apply_initial_registry(
    env: dict[str, str],
    dpi: int,
    *,
    dxva_vaapi: bool = False,
    eax: bool = False,
    gtk: bool = False,
    winrt_dark: bool = False,
    no_associations: bool = False,
    no_xdg: bool = False,
    no_mono: bool = False,
    no_gecko: bool = False,
    disable_explorer: bool = False,
    disable_services: bool = False,
) -> None:
    coros: list[Coroutine[Any, Any, None]] = []
    if dpi != DEFAULT_DPI:
        coros.append(
            _run_reg(
                env,
                r'HKCU\Control Panel\Desktop',
                '/t',
                'REG_DWORD',
                '/v',
                'LogPixels',
                '/d',
                str(dpi),
                '/f',
            ))
    if dxva_vaapi:
        coros.append(_run_reg(env, r'HKCU\Software\Wine\DXVA2', '/v', 'backend', '/d', 'va', '/f'))
    if eax:
        coros.append(
            _run_reg(env, r'HKCU\Software\Wine\DirectSound', '/v', 'EAXEnabled', '/d', 'Y', '/f'))
    if gtk:
        coros.append(_run_reg(env, r'HKCU\Software\Wine', '/v', 'ThemeEngine', '/d', 'GTK', '/f'))
    if winrt_dark:
        coros.extend(
            _run_reg(
                env,
                r'HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize',
                '/t',
                'REG_DWORD',
                '/v',
                k,
                '/d',
                '0',
                '/f',
            ) for k in ('AppsUseLightTheme', 'SystemUsesLightTheme'))
    if no_associations:
        coros.append(
            _run_reg(
                env,
                r'HKCU\Software\Wine\Explorer\FileAssociations',
                '/v',
                'Enable',
                '/d',
                'N',
                '/f',
            ))
    if no_xdg:
        coros.append(
            _run_reg(env, r'HKCU\Software\Wine\DllOverrides', '/v', 'winemenubuilder.exe', '/f'))
    if no_mono:
        coros.append(_run_reg(env, r'HKCU\Software\Wine\DllOverrides', '/v', 'mscoree', '/f'))
    if no_gecko:
        coros.append(_run_reg(env, r'HKCU\Software\Wine\DllOverrides', '/v', 'mshtml', '/f'))
    if disable_explorer:
        coros.append(_run_reg(env, r'HKCU\Software\Wine\DllOverrides', '/v', 'explorer.exe', '/f'))
    if disable_services:
        coros.append(_run_reg(env, r'HKCU\Software\Wine\DllOverrides', '/v', 'services.exe', '/f'))
    if coros:
        await asyncio.gather(*coros)


async def _setup_tmpfs(target: Path) -> None:
    username = environ.get('USER', environ.get('USERNAME', 'user'))
    user_temp = target / f'drive_c/users/{username}/Temp'
    win_temp = target / 'drive_c/windows/temp'
    await asyncio.gather(
        run_in_thread(partial(rmtree, user_temp, ignore_errors=True)),
        run_in_thread(partial(rmtree, win_temp, ignore_errors=True)),
    )
    tmpdir = tempfile.gettempdir()
    await asyncio.gather(
        AsyncPath(user_temp).symlink_to(tmpdir, target_is_directory=True),
        AsyncPath(win_temp).symlink_to(tmpdir, target_is_directory=True),
    )


async def _run_winetricks(
    prefix_name: str,
    tricks_list: list[str],
    windows_version: WineWindowsVersion,
    *,
    sandbox: bool = False,
    vd: str = 'off',
) -> None:
    tricks_list.append(WINETRICKS_VERSION_MAPPING[windows_version])
    if sandbox:
        tricks_list += ['isolate_home', 'sandbox']
    if vd != 'off':
        tricks_list.append(f'vd={vd}')
    if winetricks := await run_in_thread(partial(which, 'winetricks')):
        cmd = (
            winetricks,
            '--force',
            '--country=US',
            '--unattended',
            f'prefix={prefix_name}',
            *sorted(set(tricks_list)),
        )
        await _run_cmd(cmd)


async def _setup_dxvk_nvapi(target: Path,
                            env: dict[str, str],
                            session: niquests.AsyncSession,
                            *,
                            _32bit: bool = False) -> None:
    await _run_cmd(('setup_vkd3d_proton.sh', 'install'), env)
    version = '0.8.3'
    nvidia_libs = 'nvidia-libs'
    prefix_tar = f'{nvidia_libs}-{version}'
    r = await session.get(
        f'https://github.com/SveSop/{nvidia_libs}/releases/download/v{version}/{prefix_tar}.tar.xz',
        timeout=15,
    )
    r.raise_for_status()
    content = r.content or b''
    with xz.open(BytesIO(content)) as xz_file, tarfile.TarFile(fileobj=xz_file) as tar:
        x32_items = ('nvcuda', 'nvcuvid', 'nvencodeapi', 'nvapi')
        for item in x32_items:
            member = tar.getmember(f'{prefix_tar}/x32/{item}.dll')
            member.name = f'{item}.dll'
            await run_in_thread(
                partial(tar.extract, member, target / 'drive_c' / 'windows' / 'syswow64'))
        await asyncio.gather(
            *(_run_reg(env, r'HKCU\Software\Wine\DllOverrides', '/v', item, '/d', 'native', '/f')
              for item in x32_items))
        if not _32bit:
            x64_items = (
                'nvcuda',
                'nvoptix',
                'nvcuvid',
                'nvencodeapi64',
                'nvapi64',
                'nvofapi64',
            )
            for item in x64_items:
                member = tar.getmember(f'{prefix_tar}/x64/{item}.dll')
                member.name = f'{item}.dll'
                await run_in_thread(
                    partial(tar.extract, member, target / 'drive_c' / 'windows' / 'system32'))
            await asyncio.gather(*(_run_reg(
                env,
                r'HKCU\Software\Wine\DllOverrides',
                '/v',
                item,
                '/d',
                'native',
                '/f',
                wine_bin='wine64',
            ) for item in x64_items))
    await asyncio.gather(*(run_in_thread(
        partial(
            copyfile,
            f'/lib64/nvidia/wine/{pfx}nvngx.dll',
            target / 'drive_c' / 'windows' / 'system32' / f'{pfx}nvngx.dll',
        )) for pfx in ('', '_')))
    if not _32bit:
        await _run_reg(
            env,
            r'HKLM\Software\NVIDIA Corporation\Global\NGXCore',
            '/t',
            'REG_SZ',
            '/v',
            'FullPath',
            '/d',
            r'C:\Windows\system32',
            '/f',
            wine_bin='wine64',
        )


async def _apply_noto_sans(env: dict[str, str]) -> None:
    await asyncio.gather(*(_run_reg(
        env,
        r'HKLM\Software\Microsoft\Windows NT\CurrentVersion\FontSubstitutes',
        '/t',
        'REG_SZ',
        '/v',
        font_name,
        '/d',
        'Noto Sans',
        '/f',
    ) for font_name in _CREATE_WINE_PREFIX_NOTO_FONT_REPLACEMENTS))
    face_name = 'Noto Sans'.encode('utf-16le').ljust(LF_FULLFACESIZE, b'\0')
    coros: list[Coroutine[Any, Any, None]] = []
    for entry_name in _CREATE_WINE_PREFIX_NOTO_REGISTRY_ENTRIES:
        weight = Weight.FW_BOLD if entry_name == 'Caption' else Weight.FW_NORMAL
        packed = struct.pack(
            '=5l8B64B',
            *LOGFONTW(
                lfHeight=-12,
                lfWidth=0,
                lfEscapement=0,
                lfOrientation=0,
                lfWeight=weight,
                lfItalic=False,
                lfUnderline=False,
                lfStrikeOut=False,
                lfCharSet=CharacterSet.DEFAULT_CHARSET,
                lfOutPrecision=OutputPrecision.OUT_DEFAULT_PRECIS,
                lfClipPrecision=ClipPrecision.CLIP_DEFAULT_PRECIS,
                lfQuality=Quality.DEFAULT_QUALITY,
                lfPitchAndFamily=Pitch.VARIABLE_PITCH | Family.FF_SWISS,
            ),
            *face_name,
        )
        coros.append(
            _run_reg(
                env,
                r'HKCU\Control Panel\Desktop\WindowMetrics',
                '/t',
                'REG_BINARY',
                '/v',
                f'{entry_name}Font',
                '/d',
                ''.join(f'{x:02x}' for x in packed),
                '/f',
            ))
    await asyncio.gather(*coros)


async def _add_q4wine_prefix(prefix_name: str, target: Path) -> None:
    db_path = platformdirs.user_config_path() / 'q4wine/db/generic.dat'
    if not await AsyncPath(db_path).exists():
        return
    log.debug('Adding this prefix to Q4Wine.')
    run_string = (r'%CONSOLE_BIN% %CONSOLE_ARGS% %ENV_BIN% %ENV_ARGS% /bin/sh -c '
                  r'"%WORK_DIR% %SET_NICE% %WINE_BIN% %VIRTUAL_DESKTOP% %PROGRAM_BIN% '
                  r'%PROGRAM_ARGS% 2>&1 "')

    def _do_q4wine_insert() -> None:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute(
                'INSERT INTO prefix (name, path, mountpoint_windrive, run_string, version_id) '
                'VALUES (?, ?, ?, ?, 1)',
                (prefix_name, str(target), 'D:', run_string),
            )
            prefix_id = c.lastrowid
            if prefix_id is None:
                msg = 'Q4Wine insert did not return a prefix row ID.'
                raise RuntimeError(msg)
            log.debug('Q4Wine prefix ID: %d', prefix_id)
            for dir_name in ('system', 'autostart', 'import'):
                c.execute('INSERT INTO dir (name, prefix_id) VALUES (?, ?)', (dir_name, prefix_id))
            for args, exec_, icon_path, desc, folder, display_name in Q4WINE_DEFAULT_ICONS:
                c.execute(
                    """INSERT INTO icon (
    cmdargs, exec, icon_path, desc, dir_id, name, prefix_id, nice)
    VALUES (
        ?, ?, ?, ?, (
            SELECT id FROM dir WHERE name = ? AND prefix_id = ?
        ), ?, ?, 0
    )""",
                    (
                        args or None,
                        exec_,
                        icon_path,
                        desc,
                        folder,
                        prefix_id,
                        display_name,
                        prefix_id,
                    ),
                )
            c.execute('DELETE FROM logging WHERE prefix_id = ?', (prefix_id,))

    await run_in_thread(_do_q4wine_insert)


async def create_wine_prefix(  # noqa: PLR0913
    prefix_name: str,
    *,
    _32bit: bool = False,
    asio: bool = False,
    disable_explorer: bool = False,
    disable_services: bool = False,
    dpi: int = DEFAULT_DPI,
    dxva_vaapi: bool = False,
    dxvk_nvapi: bool = False,
    eax: bool = False,
    gtk: bool = False,
    no_associations: bool = False,
    no_gecko: bool = False,
    no_mono: bool = False,
    no_xdg: bool = False,
    noto_sans: bool = False,
    prefix_root: StrPath | None = None,
    sandbox: bool = False,
    tmpfs: bool = False,
    tricks: Iterable[str] | None = None,
    vd: str = 'off',
    windows_version: WineWindowsVersion = '10',
    winrt_dark: bool = False,
) -> Path:
    """
    Create a Wine prefix with custom settings.

    If winetricks is not installed, the ``tricks`` argument will be ignored.

    Parameters
    ----------
    prefix_name : str
        Name of the prefix to create.
    _32bit : bool
        Create a 32-bit Wine prefix.
    asio : bool
        Enable ASIO support.
    disable_explorer : bool
        Disable ``explorer.exe`` from automatically starting.
    disable_services : bool
        Disable ``services.exe`` from automatically starting.
    dpi : int
        Screen DPI.
    dxva_vaapi : bool
        Enable VAAPI support for DXVA.
    dxvk_nvapi : bool
        Enable DXVK NVAPI support.
    eax : bool
        Enable EAX support.
    gtk : bool
        Enable GTK theme support.
    no_associations : bool
        Disable file associations.
    no_gecko : bool
        Disable Gecko support.
    no_mono : bool
        Disable Mono support.
    no_xdg : bool
        Disable XDG support.
    noto_sans : bool
        Use Noto Sans font.
    prefix_root : str | PathLike[str] | None
        Root directory for the prefix. If ``None``, defaults to ``~/.local/share/wineprefixes``.
    sandbox : bool
        Enable sandbox mode.
    tmpfs : bool
        Use ``/tmp`` as a temporary filesystem.
    tricks : Iterable[str] | None
        List of winetricks to run. If ``None``, defaults to an empty list.
    vd : str
        Virtual desktop mode. If ``'off'``, disables virtual desktop mode.
    windows_version : WineWindowsVersion
        Windows version to set for the prefix.
    winrt_dark : bool
        Enable Windows 10 dark mode.

    Returns
    -------
    Path
        Path to the created prefix.

    Raises
    ------
    FileExistsError
        If the prefix directory already exists.
    """
    tricks_list = list((t for t in tricks
                        if t not in WINETRICKS_VERSION_MAPPING.values() and not t.startswith('vd=')
                        ) if tricks else [])
    root = Path(prefix_root) if prefix_root else Path.home() / '.local/share/wineprefixes'
    await AsyncPath(root).mkdir(parents=True, exist_ok=True)
    target = root / prefix_name
    if await AsyncPath(target).exists():
        raise FileExistsError
    if 'DISPLAY' not in environ or 'XAUTHORITY' not in environ:
        log.warning(
            'Wine will likely fail to run since DISPLAY or XAUTHORITY are not in the environment.')
    env = _build_prefix_env(target, _32bit=_32bit)
    await _run_cmd(('wineboot', '--init'), env)
    await _run_cmd(('wineserver', '-w'), env)
    coros: list[Coroutine[Any, Any, None]] = [
        _apply_initial_registry(
            env,
            dpi,
            disable_explorer=disable_explorer,
            disable_services=disable_services,
            dxva_vaapi=dxva_vaapi,
            eax=eax,
            gtk=gtk,
            no_associations=no_associations,
            no_gecko=no_gecko,
            no_mono=no_mono,
            no_xdg=no_xdg,
            winrt_dark=winrt_dark,
        )
    ]
    if tmpfs:
        coros.append(_setup_tmpfs(target))
    await asyncio.gather(*coros)
    if dxvk_nvapi:
        tricks_list.append('dxvk')
    try:
        await _run_winetricks(prefix_name, tricks_list, windows_version, sandbox=sandbox, vd=vd)
    except sp.CalledProcessError as e:  # pragma: no cover
        log.warning('Winetricks exit code was %d but it may have succeeded.', e.returncode)
    if dxvk_nvapi:
        async with niquests.AsyncSession() as session:
            await _setup_dxvk_nvapi(target, env, session, _32bit=_32bit)
    if noto_sans:
        await _apply_noto_sans(env)
    if asio:
        if register := await run_in_thread(partial(which, 'wineasio-register')):
            log.debug('Running: %s', register)
            await _run_cmd((register,), env)
        else:
            log.warning('Skipping ASIO setup because wineasio-register is not in PATH.')
    await _add_q4wine_prefix(prefix_name, target)
    return target

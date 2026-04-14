# ruff: noqa: S108
from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock

from mkwineprefix.prefix import create_wine_prefix
import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def _mock_async_subprocess(mocker: MockerFixture, *,
                           fail_cmds: frozenset[str] = frozenset()) -> AsyncMock:
    """Set up a mock for ``asyncio.create_subprocess_exec``."""
    async def _create_subprocess(*args: Any, **_kwargs: Any) -> AsyncMock:
        proc = AsyncMock()
        proc.wait.return_value = 1 if args and args[0] in fail_cmds else 0
        return proc

    return mocker.patch('asyncio.create_subprocess_exec', side_effect=_create_subprocess)


def _mock_anyio_path(mocker: MockerFixture, *, exists: bool = False) -> Any:
    """Set up a mock for ``anyio.Path``."""
    mock_anyio_path_cls = mocker.patch('mkwineprefix.prefix.AsyncPath')
    mock_instance = mocker.Mock()
    mock_instance.exists = AsyncMock(return_value=exists)
    mock_instance.mkdir = AsyncMock()
    mock_instance.symlink_to = AsyncMock()
    mock_anyio_path_cls.return_value = mock_instance
    return mock_anyio_path_cls


async def test_create_wine_prefix_basic(mocker: MockerFixture) -> None:
    mock_subprocess = _mock_async_subprocess(mocker)
    mocker.patch('mkwineprefix.prefix.which', return_value=None)
    mocker.patch('mkwineprefix.prefix.niquests.AsyncSession')
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mocker.patch('mkwineprefix.prefix.xz.open')
    mocker.patch('mkwineprefix.prefix.tarfile.TarFile')
    mocker.patch('mkwineprefix.prefix.copyfile')
    mocker.patch('mkwineprefix.prefix.platformdirs.user_config_path')
    mocker.patch('mkwineprefix.prefix.sqlite3.connect')
    _mock_anyio_path(mocker)
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value = mock_path
    mocker.patch('mkwineprefix.prefix.rmtree')
    mocker.patch('mkwineprefix.prefix.tempfile.gettempdir', return_value='/tmp')
    mocker.patch('mkwineprefix.prefix.struct.pack', return_value=b'\x00' * 92)
    mocker.patch.dict(
        'mkwineprefix.prefix.environ',
        {
            'PATH': '/bin',
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/.Xauthority'
        },
        clear=True,
    )
    result = await create_wine_prefix('test-prefix')
    assert result is not None
    assert mock_subprocess.call_count > 0


async def test_create_wine_prefix_raises_if_exists(mocker: MockerFixture) -> None:
    _mock_anyio_path(mocker, exists=True)
    mocker.patch('mkwineprefix.prefix.Path')
    with pytest.raises(FileExistsError):
        await create_wine_prefix('already-exists')


async def test_create_wine_prefix_with_tricks_and_winetricks(mocker: MockerFixture) -> None:
    mock_subprocess = _mock_async_subprocess(mocker)
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mocker.patch('mkwineprefix.prefix.which', return_value='/usr/bin/winetricks')
    _mock_anyio_path(mocker)
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value = mock_path
    mocker.patch.dict(
        'mkwineprefix.prefix.environ',
        {
            'PATH': '/bin',
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/.Xauthority'
        },
        clear=True,
    )
    await create_wine_prefix('prefix2', tricks=['corefonts', 'win10'])
    assert any(
        args[0][0] == '/usr/bin/winetricks' for args in mock_subprocess.call_args_list if args[0])


async def test_create_wine_prefix_with_options(mocker: MockerFixture) -> None:
    mock_subprocess = _mock_async_subprocess(mocker)
    mocker.patch('mkwineprefix.prefix.which', return_value=None)
    _mock_anyio_path(mocker)
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value = mock_path
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mocker.patch('mkwineprefix.prefix.struct.pack', return_value=b'\x00' * 92)
    mocker.patch.dict(
        'mkwineprefix.prefix.environ',
        {
            'PATH': '/bin',
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/.Xauthority'
        },
        clear=True,
    )
    await create_wine_prefix(
        'prefix3',
        _32bit=True,
        asio=True,
        disable_explorer=True,
        disable_services=True,
        dpi=120,
        dxva_vaapi=True,
        dxvk_nvapi=False,
        eax=True,
        gtk=True,
        no_associations=True,
        no_gecko=True,
        no_mono=True,
        no_xdg=True,
        noto_sans=True,
        sandbox=True,
        tmpfs=True,
        tricks=['corefonts'],
        vd='1024x768',
        windows_version='7',
        winrt_dark=True,
    )
    assert mock_subprocess.call_count > 5


async def test_create_wine_prefix_handles_winetricks_failure(mocker: MockerFixture) -> None:
    _mock_async_subprocess(mocker, fail_cmds=frozenset({'/usr/bin/winetricks'}))
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mocker.patch('mkwineprefix.prefix.which', return_value='/usr/bin/winetricks')
    _mock_anyio_path(mocker)
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value = mock_path
    mocker.patch('mkwineprefix.prefix.logging.getLogger', return_value=mocker.Mock())
    mocker.patch.dict(
        'mkwineprefix.prefix.environ',
        {
            'PATH': '/bin',
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/.Xauthority'
        },
        clear=True,
    )
    await create_wine_prefix('prefix4', tricks=['corefonts'])


async def test_create_wine_prefix_dxvk_nvapi_true_no_q4wine_db(mocker: MockerFixture) -> None:
    mock_subprocess = _mock_async_subprocess(mocker)
    mocker.patch(
        'mkwineprefix.prefix.which',
        side_effect=lambda x: '/usr/bin/winetricks' if x == 'winetricks' else None,
    )
    mock_session = AsyncMock()
    mock_response = mocker.Mock()
    mock_response.content = b''
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session_cls = mocker.patch('mkwineprefix.prefix.niquests.AsyncSession')
    mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=None)
    mocker.patch('mkwineprefix.prefix.xz.open')
    mocker.patch('mkwineprefix.prefix.tarfile.TarFile')
    mocker.patch('mkwineprefix.prefix.copyfile')
    mocker.patch('mkwineprefix.prefix.struct.pack', return_value=b'\x00' * 92)
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mocker.patch.dict('mkwineprefix.prefix.environ', {
        'PATH': '/bin',
        'XAUTHORITY': '/tmp/.Xauthority'
    },
                      clear=True)
    mock_anyio_path_cls = _mock_anyio_path(mocker)
    mock_q4wine_path = mocker.Mock()
    mock_q4wine_path.exists = AsyncMock(return_value=False)

    def _anyio_path_factory(path: Any) -> Any:
        path_str = str(path)
        if 'q4wine' in path_str:
            return mock_q4wine_path
        mock = mocker.Mock()
        mock.exists = AsyncMock(return_value=False)
        mock.mkdir = AsyncMock()
        mock.symlink_to = AsyncMock()
        return mock

    mock_anyio_path_cls.side_effect = _anyio_path_factory
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value = mock_path
    mocker.patch('mkwineprefix.prefix.rmtree')
    mocker.patch('mkwineprefix.prefix.tempfile.gettempdir', return_value='/tmp')
    result = await create_wine_prefix('dxvk-prefix', dxvk_nvapi=True)
    assert result is not None
    assert any(
        args[0][0] == 'setup_vkd3d_proton.sh' for args in mock_subprocess.call_args_list if args[0])


async def test_create_wine_prefix_dxvk_nvapi_true_32bit(mocker: MockerFixture) -> None:
    mock_subprocess = _mock_async_subprocess(mocker)
    mocker.patch(
        'mkwineprefix.prefix.which',
        side_effect=lambda x: '/usr/bin/winetricks' if x == 'winetricks' else None,
    )
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mock_session = AsyncMock()
    mock_response = mocker.Mock()
    mock_response.content = b''
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session_cls = mocker.patch('mkwineprefix.prefix.niquests.AsyncSession')
    mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=None)
    mocker.patch('mkwineprefix.prefix.xz.open')
    mocker.patch('mkwineprefix.prefix.tarfile.TarFile')
    mocker.patch('mkwineprefix.prefix.copyfile')
    mocker.patch('mkwineprefix.prefix.struct.pack', return_value=b'\x00' * 92)
    mocker.patch.dict(
        'mkwineprefix.prefix.environ',
        {
            'PATH': '/bin',
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/.Xauthority'
        },
        clear=True,
    )
    mock_anyio_path_cls = _mock_anyio_path(mocker)
    mock_q4wine_path = mocker.Mock()
    mock_q4wine_path.exists = AsyncMock(return_value=False)

    def _anyio_path_factory(path: Any) -> Any:
        path_str = str(path)
        if 'q4wine' in path_str:
            return mock_q4wine_path
        mock = mocker.Mock()
        mock.exists = AsyncMock(return_value=False)
        mock.mkdir = AsyncMock()
        mock.symlink_to = AsyncMock()
        return mock

    mock_anyio_path_cls.side_effect = _anyio_path_factory
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value = mock_path
    mocker.patch('mkwineprefix.prefix.rmtree')
    mocker.patch('mkwineprefix.prefix.tempfile.gettempdir', return_value='/tmp')
    result = await create_wine_prefix('dxvk-prefix-32', dxvk_nvapi=True, _32bit=True)
    assert result is not None
    assert any(
        args[0][0] == 'setup_vkd3d_proton.sh' for args in mock_subprocess.call_args_list if args[0])
    assert not any(args[0][0] == 'wine64' and len(args[0]) > 4 and 'NGXCore' in str(args[0])
                   for args in mock_subprocess.call_args_list if args[0])


async def test_create_wine_prefix_asio_true_register_found(mocker: MockerFixture) -> None:
    mock_subprocess = _mock_async_subprocess(mocker)
    mocker.patch(
        'mkwineprefix.prefix.which',
        side_effect=lambda x: '/usr/bin/wineasio-register' if x == 'wineasio-register' else None,
    )
    _mock_anyio_path(mocker)
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value = mock_path
    mocker.patch.dict(
        'mkwineprefix.prefix.environ',
        {
            'PATH': '/bin',
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/.Xauthority'
        },
        clear=True,
    )
    mocker.patch('mkwineprefix.prefix.niquests.AsyncSession')
    mocker.patch('mkwineprefix.prefix.xz.open')
    mocker.patch('mkwineprefix.prefix.tarfile.TarFile')
    mocker.patch('mkwineprefix.prefix.copyfile')
    mocker.patch('mkwineprefix.prefix.platformdirs.user_config_path')
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mocker.patch('mkwineprefix.prefix.rmtree')
    mocker.patch('mkwineprefix.prefix.tempfile.gettempdir', return_value='/tmp')
    mocker.patch('mkwineprefix.prefix.struct.pack', return_value=b'\x00' * 92)
    result = await create_wine_prefix('asio-prefix', asio=True)
    assert result is not None
    assert any(args[0][0] == '/usr/bin/wineasio-register' for args in mock_subprocess.call_args_list
               if args[0])


async def test_create_wine_prefix_q4wine_missing_row_id(mocker: MockerFixture) -> None:
    _mock_async_subprocess(mocker)
    mocker.patch('mkwineprefix.prefix.which', return_value=None)
    mocker.patch('mkwineprefix.prefix.niquests.AsyncSession')
    mocker.patch('mkwineprefix.prefix.xz.open')
    mocker.patch('mkwineprefix.prefix.tarfile.TarFile')
    mocker.patch('mkwineprefix.prefix.copyfile')
    mock_user_config_path = mocker.patch('mkwineprefix.prefix.platformdirs.user_config_path')
    mock_db_path = mocker.Mock()
    mock_db_path.__str__ = lambda _self: '/config/q4wine/db/generic.dat'
    mock_db_path.exists.return_value = True
    mock_user_config_path.return_value.__truediv__.return_value = mock_db_path
    mock_cursor = mocker.Mock()
    mock_cursor.lastrowid = None
    mock_conn = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = mocker.Mock(return_value=mock_conn)
    mock_conn.__exit__ = mocker.Mock(return_value=None)
    mocker.patch('mkwineprefix.prefix.sqlite3.connect', return_value=mock_conn)
    mock_anyio_path_cls = _mock_anyio_path(mocker)
    mock_q4wine_path = mocker.Mock()
    mock_q4wine_path.exists = AsyncMock(return_value=True)

    def _anyio_path_factory(path: Any) -> Any:
        path_str = str(path)
        if 'q4wine' in path_str:
            return mock_q4wine_path
        mock = mocker.Mock()
        mock.exists = AsyncMock(return_value=False)
        mock.mkdir = AsyncMock()
        mock.symlink_to = AsyncMock()
        return mock

    mock_anyio_path_cls.side_effect = _anyio_path_factory
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value = mock_path
    mocker.patch('mkwineprefix.prefix.rmtree')
    mocker.patch('mkwineprefix.prefix.tempfile.gettempdir', return_value='/tmp')
    mocker.patch('mkwineprefix.prefix.struct.pack', return_value=b'\x00' * 92)
    mocker.patch.dict(
        'mkwineprefix.prefix.environ',
        {
            'PATH': '/bin',
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/.Xauthority'
        },
        clear=True,
    )
    with pytest.raises(RuntimeError, match='Q4Wine insert did not return a prefix row ID'):
        await create_wine_prefix('q4wine-bad-id')


async def test_create_wine_prefix_reg_failure(mocker: MockerFixture) -> None:
    _mock_async_subprocess(mocker, fail_cmds=frozenset({'wine'}))
    mocker.patch('mkwineprefix.prefix.which', return_value=None)
    _mock_anyio_path(mocker)
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value = mock_path
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mocker.patch.dict(
        'mkwineprefix.prefix.environ',
        {
            'PATH': '/bin',
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/.Xauthority'
        },
        clear=True,
    )
    import subprocess as sp
    with pytest.raises(sp.CalledProcessError):
        await create_wine_prefix('reg-fail', dpi=120)


async def test_create_wine_prefix_q4wine_success(mocker: MockerFixture) -> None:
    _mock_async_subprocess(mocker)
    mocker.patch('mkwineprefix.prefix.which', return_value=None)
    mocker.patch('mkwineprefix.prefix.niquests.AsyncSession')
    mocker.patch('mkwineprefix.prefix.xz.open')
    mocker.patch('mkwineprefix.prefix.tarfile.TarFile')
    mocker.patch('mkwineprefix.prefix.copyfile')
    mock_user_config_path = mocker.patch('mkwineprefix.prefix.platformdirs.user_config_path')
    mock_db_path = mocker.Mock()
    mock_db_path.__str__ = lambda _self: '/config/q4wine/db/generic.dat'
    mock_db_path.exists.return_value = True
    mock_user_config_path.return_value.__truediv__.return_value = mock_db_path
    mock_cursor = mocker.Mock()
    mock_cursor.lastrowid = 42
    mock_conn = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = mocker.Mock(return_value=mock_conn)
    mock_conn.__exit__ = mocker.Mock(return_value=None)
    mocker.patch('mkwineprefix.prefix.sqlite3.connect', return_value=mock_conn)
    mock_anyio_path_cls = _mock_anyio_path(mocker)
    mock_q4wine_path = mocker.Mock()
    mock_q4wine_path.exists = AsyncMock(return_value=True)

    def _anyio_path_factory(path: Any) -> Any:
        path_str = str(path)
        if 'q4wine' in path_str:
            return mock_q4wine_path
        mock = mocker.Mock()
        mock.exists = AsyncMock(return_value=False)
        mock.mkdir = AsyncMock()
        mock.symlink_to = AsyncMock()
        return mock

    mock_anyio_path_cls.side_effect = _anyio_path_factory
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value = mock_path
    mocker.patch('mkwineprefix.prefix.rmtree')
    mocker.patch('mkwineprefix.prefix.tempfile.gettempdir', return_value='/tmp')
    mocker.patch('mkwineprefix.prefix.struct.pack', return_value=b'\x00' * 92)
    mocker.patch.dict(
        'mkwineprefix.prefix.environ',
        {
            'PATH': '/bin',
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/.Xauthority'
        },
        clear=True,
    )
    result = await create_wine_prefix('q4wine-ok')
    assert result is not None
    assert mock_cursor.execute.call_count > 3

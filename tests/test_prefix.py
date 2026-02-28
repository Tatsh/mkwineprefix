# ruff: noqa: S108
from __future__ import annotations

from typing import TYPE_CHECKING, Any
import subprocess as sp

from mkwineprefix.prefix import create_wine_prefix
import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_create_wine_prefix_basic(mocker: MockerFixture) -> None:
    sp_run = mocker.patch('mkwineprefix.prefix.sp.run')
    mocker.patch('mkwineprefix.prefix.which', return_value=None)
    mocker.patch('mkwineprefix.prefix.requests.get')
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mocker.patch('mkwineprefix.prefix.xz.open')
    mocker.patch('mkwineprefix.prefix.tarfile.TarFile')
    mocker.patch('mkwineprefix.prefix.copyfile')
    mocker.patch('mkwineprefix.prefix.platformdirs.user_config_path')
    mocker.patch('mkwineprefix.prefix.sqlite3.connect')
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value.__truediv__.return_value.exists.return_value = False  # noqa: E501
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
    result = create_wine_prefix('test-prefix')
    assert result is not None
    assert sp_run.call_count > 0


def test_create_wine_prefix_raises_if_exists(mocker: MockerFixture) -> None:
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value.__truediv__.return_value.exists.return_value = True  # noqa: E501
    with pytest.raises(FileExistsError):
        create_wine_prefix('already-exists')


def test_create_wine_prefix_with_tricks_and_winetricks(mocker: MockerFixture) -> None:
    sp_run = mocker.patch('mkwineprefix.prefix.sp.run')
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mocker.patch('mkwineprefix.prefix.which', return_value='/usr/bin/winetricks')
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value.__truediv__.return_value.exists.return_value = False  # noqa: E501
    mocker.patch.dict(
        'mkwineprefix.prefix.environ',
        {
            'PATH': '/bin',
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/.Xauthority'
        },
        clear=True,
    )
    create_wine_prefix('prefix2', tricks=['corefonts', 'win10'])
    assert any('/usr/bin/winetricks' in str(args[0]) for args in sp_run.call_args_list)


def test_create_wine_prefix_with_options(mocker: MockerFixture) -> None:
    sp_run = mocker.patch('mkwineprefix.prefix.sp.run')
    mocker.patch('mkwineprefix.prefix.which', return_value=None)
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value.__truediv__.return_value.exists.return_value = False  # noqa: E501
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
    create_wine_prefix(
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
    assert sp_run.call_count > 5


def test_create_wine_prefix_handles_winetricks_failure(mocker: MockerFixture) -> None:
    sp_run = mocker.patch('mkwineprefix.prefix.sp.run')
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mocker.patch('mkwineprefix.prefix.which', return_value='/usr/bin/winetricks')
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    mock_path.home.return_value.__truediv__.return_value.__truediv__.return_value.exists.return_value = False  # noqa: E501
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

    def run_side_effect(*args: Any, **kwargs: Any) -> None:
        if args[0] == '/usr/bin/winetricks':
            raise sp.CalledProcessError(1, 'winetricks', '', '')

    sp_run.side_effect = run_side_effect
    create_wine_prefix('prefix4', tricks=['corefonts'])


def test_create_wine_prefix_dxvk_nvapi_true_no_q4wine_db(mocker: MockerFixture) -> None:
    sp_run = mocker.patch('mkwineprefix.prefix.sp.run')
    mocker.patch(
        'mkwineprefix.prefix.which',
        side_effect=lambda x: '/usr/bin/winetricks' if x == 'winetricks' else None,
    )
    mock_get = mocker.patch('mkwineprefix.prefix.requests.get')
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
    mock_user_config_path = mocker.patch('mkwineprefix.prefix.platformdirs.user_config_path')
    mock_db_path = mocker.Mock()
    mock_db_path.exists.return_value = False
    mock_user_config_path.return_value.__truediv__.return_value = mock_db_path
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    prefix_root = mock_path.home.return_value.__truediv__.return_value.__truediv__.return_value
    prefix_root.exists.return_value = False
    mocker.patch('mkwineprefix.prefix.rmtree')
    mocker.patch('mkwineprefix.prefix.tempfile.gettempdir', return_value='/tmp')
    mock_get.return_value.content = b''
    mocker.patch('mkwineprefix.prefix.xz.open')
    result = create_wine_prefix('dxvk-prefix', dxvk_nvapi=True)
    assert result is not None
    assert any('setup_vkd3d_proton.sh' in str(args[0]) for args in sp_run.call_args_list)


def test_create_wine_prefix_dxvk_nvapi_true_32bit(mocker: MockerFixture) -> None:
    sp_run = mocker.patch('mkwineprefix.prefix.sp.run')
    mocker.patch(
        'mkwineprefix.prefix.which',
        side_effect=lambda x: '/usr/bin/winetricks' if x == 'winetricks' else None,
    )
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mock_get = mocker.patch('mkwineprefix.prefix.requests.get')
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
    mock_user_config_path = mocker.patch('mkwineprefix.prefix.platformdirs.user_config_path')
    mock_db_path = mocker.Mock()
    mock_db_path.exists.return_value = False
    mock_user_config_path.return_value.__truediv__.return_value = mock_db_path
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    prefix_root = mock_path.home.return_value.__truediv__.return_value.__truediv__.return_value
    prefix_root.exists.return_value = False
    mocker.patch('mkwineprefix.prefix.rmtree')
    mocker.patch('mkwineprefix.prefix.tempfile.gettempdir', return_value='/tmp')
    mock_get.return_value.content = b''
    mocker.patch('mkwineprefix.prefix.xz.open')
    result = create_wine_prefix('dxvk-prefix-32', dxvk_nvapi=True, _32bit=True)
    assert result is not None
    assert any('setup_vkd3d_proton.sh' in str(args[0]) for args in sp_run.call_args_list)
    assert not any(
        isinstance(args[0], tuple) and args[0][0] == 'wine64' and 'NGXCore' in args[0]
        for args in sp_run.call_args_list)


def test_create_wine_prefix_asio_true_register_found(mocker: MockerFixture) -> None:
    sp_run = mocker.patch('mkwineprefix.prefix.sp.run')
    mocker.patch(
        'mkwineprefix.prefix.which',
        side_effect=lambda x: '/usr/bin/wineasio-register' if x == 'wineasio-register' else None,
    )
    mock_path = mocker.patch('mkwineprefix.prefix.Path')
    prefix = mock_path.home.return_value.__truediv__.return_value.__truediv__.return_value
    prefix.exists.return_value = False
    mocker.patch.dict(
        'mkwineprefix.prefix.environ',
        {
            'PATH': '/bin',
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/.Xauthority'
        },
        clear=True,
    )
    mocker.patch('mkwineprefix.prefix.requests.get')
    mocker.patch('mkwineprefix.prefix.xz.open')
    mocker.patch('mkwineprefix.prefix.tarfile.TarFile')
    mocker.patch('mkwineprefix.prefix.copyfile')
    mocker.patch('mkwineprefix.prefix.platformdirs.user_config_path')
    mocker.patch('mkwineprefix.prefix.sqlite3')
    mocker.patch('mkwineprefix.prefix.rmtree')
    mocker.patch('mkwineprefix.prefix.tempfile.gettempdir', return_value='/tmp')
    mocker.patch('mkwineprefix.prefix.struct.pack', return_value=b'\x00' * 92)
    result = create_wine_prefix('asio-prefix', asio=True)
    assert result is not None
    assert any(
        isinstance(args.args[0], tuple) and args.args[0][0] == '/usr/bin/wineasio-register'
        for args in sp_run.call_args_list)

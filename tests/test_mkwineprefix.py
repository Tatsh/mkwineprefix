from __future__ import annotations

from typing import TYPE_CHECKING
import subprocess as sp

from mkwineprefix.main import main
import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner
    from pytest_mock import MockerFixture


@pytest.fixture
def fake_prefix(tmp_path: Path) -> Path:
    return tmp_path / 'test-prefix'


def test_mkwineprefix_success(mocker: MockerFixture, runner: CliRunner, fake_prefix: Path) -> None:
    create_wine_prefix = mocker.patch('mkwineprefix.main.create_wine_prefix',
                                      return_value=str(fake_prefix))
    result = runner.invoke(main, ['test-prefix', '--dpi', '120'])
    assert result.exit_code == 0
    create_wine_prefix.assert_called_once()


def test_mkwineprefix_file_exists(mocker: MockerFixture, runner: CliRunner) -> None:
    mocker.patch('mkwineprefix.main.create_wine_prefix', side_effect=FileExistsError)
    result = runner.invoke(main, ['test-prefix'])
    assert result.exit_code != 0


def test_mkwineprefix_subprocess_error(mocker: MockerFixture, runner: CliRunner) -> None:
    mocker.Mock(stderr='err', stdout='out')
    mocker.patch(
        'mkwineprefix.main.create_wine_prefix',
        side_effect=sp.CalledProcessError(1, 'cmd', stderr='err', output='out'),
    )
    result = runner.invoke(main, ['test-prefix'])
    assert result.exit_code != 0

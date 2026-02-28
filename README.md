# mkwineprefix

[![Python versions](https://img.shields.io/pypi/pyversions/mkwineprefix.svg?color=blue&logo=python&logoColor=white)](https://www.python.org/)
[![PyPI - Version](https://img.shields.io/pypi/v/mkwineprefix)](https://pypi.org/project/mkwineprefix/)
[![GitHub tag (with filter)](https://img.shields.io/github/v/tag/Tatsh/mkwineprefix)](https://github.com/Tatsh/mkwineprefix/tags)
[![License](https://img.shields.io/github/license/Tatsh/mkwineprefix)](https://github.com/Tatsh/mkwineprefix/blob/master/LICENSE.txt)
[![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/Tatsh/mkwineprefix/v0.0.1/master)](https://github.com/Tatsh/mkwineprefix/compare/v0.0.1...master)
[![CodeQL](https://github.com/Tatsh/mkwineprefix/actions/workflows/codeql.yml/badge.svg)](https://github.com/Tatsh/mkwineprefix/actions/workflows/codeql.yml)
[![QA](https://github.com/Tatsh/mkwineprefix/actions/workflows/qa.yml/badge.svg)](https://github.com/Tatsh/mkwineprefix/actions/workflows/qa.yml)
[![Tests](https://github.com/Tatsh/mkwineprefix/actions/workflows/tests.yml/badge.svg)](https://github.com/Tatsh/mkwineprefix/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Tatsh/mkwineprefix/badge.svg?branch=master)](https://coveralls.io/github/Tatsh/mkwineprefix?branch=master)
[![Dependabot](https://img.shields.io/badge/Dependabot-enabled-blue?logo=dependabot)](https://github.com/dependabot)
[![Documentation Status](https://readthedocs.org/projects/mkwineprefix/badge/?version=latest)](https://mkwineprefix.readthedocs.org/?badge=latest)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Poetry](https://img.shields.io/badge/Poetry-242d3e?logo=poetry)](https://python-poetry.org)
[![pydocstyle](https://img.shields.io/badge/pydocstyle-enabled-AD4CD3?logo=pydocstyle)](https://www.pydocstyle.org/)
[![pytest](https://img.shields.io/badge/pytest-enabled-CFB97D?logo=pytest)](https://docs.pytest.org)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Downloads](https://static.pepy.tech/badge/mkwineprefix/month)](https://pepy.tech/project/mkwineprefix)
[![Stargazers](https://img.shields.io/github/stars/Tatsh/mkwineprefix?logo=github&style=flat)](https://github.com/Tatsh/mkwineprefix/stargazers)
[![Prettier](https://img.shields.io/badge/Prettier-enabled-black?logo=prettier)](https://prettier.io/)

[![@Tatsh](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpublic.api.bsky.app%2Fxrpc%2Fapp.bsky.actor.getProfile%2F%3Factor=did%3Aplc%3Auq42idtvuccnmtl57nsucz72&query=%24.followersCount&label=Follow+%40Tatsh&logo=bluesky&style=social)](https://bsky.app/profile/Tatsh.bsky.social)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Tatsh-black?logo=buymeacoffee)](https://buymeacoffee.com/Tatsh)
[![Libera.Chat](https://img.shields.io/badge/Libera.Chat-Tatsh-black?logo=liberadotchat)](irc://irc.libera.chat/Tatsh)
[![Mastodon Follow](https://img.shields.io/mastodon/follow/109370961877277568?domain=hostux.social&style=social)](https://hostux.social/@Tatsh)
[![Patreon](https://img.shields.io/badge/Patreon-Tatsh2-F96854?logo=patreon)](https://www.patreon.com/Tatsh2)

Create a Wine prefix with custom settings.

Use with eval: `eval $(mkwineprefix ...)`.

## Installation

```bash
pip install mkwineprefix
```

## Usage

Invoke with `mkwineprefix` or `python -m mkwineprefix`.

```plain
Usage: mkwineprefix [OPTIONS] PREFIX_NAME

  Create a Wine prefix with custom settings.

  This should be used with eval: eval $(mkwineprefix ...)

Options:
  -D, --dpi INTEGER               DPI.
  -d, --debug                     Enable debug output.
  --disable-explorer              Disable starting explorer.exe automatically.
  --disable-services              Disable starting services.exe automatically
                                  (only useful for simple CLI programs with
                                  --disable-explorer).
  -E, --eax                       Enable EAX.
  -g, --gtk                       Enable Gtk+ theming.
  -r, --prefix-root PATH          Prefix root.
  -S, --sandbox                   Sandbox the prefix.
  --no-gecko                      Disable downloading Gecko automatically.
  --no-mono                       Disable downloading Mono automatically.
  --no-xdg                        Disable winemenubuilder.exe.
  --no-assocs                     Disable creating file associations, but
                                  still allow menu entries to be made (unless
                                  --no-xdg is also passed).
  -N, --nvapi                     Add dxvk-nvapi.
  -o, --noto                      Use Noto Sans in place of most fonts.
  -T, --trick TEXT                Add an argument for winetricks.
  -t, --tmpfs                     Make Wine use tmpfs.
  -V, --windows-version [11|10|vista|2k3|7|8|xp|81|2k|98|95]
                                  Windows version.
  --vd SIZE                       Virtual desktop size, e.g. 1024x768.
  -W, --winrt-dark                Enable dark mode for WinRT apps.
  -x, --dxva-vaapi                Enable DXVA2 support with VA-API.
  --32                            Use 32-bit prefix.
  -h, --help                      Show this message and exit.
```

Run `mkwineprefix --help` for options.

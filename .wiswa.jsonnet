local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Create a Wine prefix with custom settings.',
  keywords: ['command line', 'dxvk', 'nvapi', 'wine', 'wine prefix'],
  project_name: 'mkwineprefix',
  version: '0.0.1',
  want_main: true,
  want_flatpak: true,
  publishing+: { flathub: 'sh.tat.mkwineprefix' },
  python_deps+: {
    tests+: {
      'pytest-asyncio': utils.latestPypiPackageVersionCaret('pytest-asyncio'),
    },
  },
  pyproject+: {
    tool+: {
      poetry+: {
        dependencies+: {
          anyio: utils.latestPypiPackageVersionCaret('anyio'),
          niquests: utils.latestPypiPackageVersionCaret('niquests'),
          platformdirs: utils.latestPypiPackageVersionCaret('platformdirs'),
          'python-xz': utils.latestPypiPackageVersionCaret('python-xz'),
        },
      },
      pytest+: {
        ini_options+: {
          asyncio_mode: 'auto',
        },
      },
    },
  },
}

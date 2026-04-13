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
  pyproject+: {
    tool+: {
      poetry+: {
        dependencies+: {
          platformdirs: utils.latestPypiPackageVersionCaret('platformdirs'),
          'python-xz': utils.latestPypiPackageVersionCaret('python-xz'),
          requests: utils.latestPypiPackageVersionCaret('requests'),
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-requests': utils.latestPypiPackageVersionCaret('types-requests'),
            },
          },
        },
      },
    },
  },
}

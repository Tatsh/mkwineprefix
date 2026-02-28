local utils = import 'utils.libjsonnet';

{
  description: 'Create a Wine prefix with custom settings.',
  keywords: ['command line', 'wine', 'wineprefix'],
  project_name: 'mkwineprefix',
  version: '0.0.0',
  want_main: true,
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
  copilot: {
    intro: 'mkwineprefix creates a Wine prefix with custom settings.',
  },
}

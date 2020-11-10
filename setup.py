# -*- coding: utf-8 -*-

import distutils.cmd
import os
import subprocess
from io import open

from setuptools import setup


class WebpackBuildCommand(distutils.cmd.Command):

    description = "Generate static assets"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if not 'CI' in os.environ and not 'TOX_ENV_NAME' in os.environ:
            # When running build inside ReadTheDocs this env variable must be set to True.
            # https://docs.readthedocs.io/en/stable/faq.html#how-do-i-change-behavior-when-building-with-read-the-docs
            if os.environ.get('READTHEDOCS') == 'True':
                # Readthedocs ships with a very old version of NPM(3.5.2) that causes npm install
                # to fail. So we first install an updated version of npm and run install.
                # Remove the below command once we have recent enough version of npm in readthedocs
                # build image.
                subprocess.run(['mkdir', '-p', '/home/docs/.npm_global'])
                subprocess.run(['npm', 'config', 'set', 'prefix', '/home/docs/.npm_global'])
                subprocess.run(['npm', 'install', '-g', 'npm@6.14.8'])
                subprocess.run(['/home/docs/.npm_global/bin/npm', 'install'], check=True)
            else:
                subprocess.run(['npm', 'install'], check=True)
            subprocess.run(['node_modules/.bin/webpack', '--config', 'webpack.prod.js'], check=True)


class WebpackDevelopCommand(distutils.cmd.Command):

    description = "Run Webpack dev server"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        subprocess.run(
            ["node_modules/.bin/webpack-dev-server", "--open", "--config", "webpack.dev.js"],
            check=True
        )


class UpdateTranslationsCommand(distutils.cmd.Command):

    description = "Run all localization commands"

    user_options = []
    sub_commands = [
        ('extract_messages', None),
        ('update_catalog', None),
        ('transifex', None),
        ('compile_catalog', None),
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)


class TransifexCommand(distutils.cmd.Command):

    description = "Update translation files through Transifex"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        subprocess.run(['tx', 'push', '--source'], check=True)
        subprocess.run(['tx', 'pull', '--mode', 'onlyreviewed', '-f', '-a'], check=True)


setup(
    version='2.99.0',
    cmdclass={
        'update_translations': UpdateTranslationsCommand,
        'transifex': TransifexCommand,
        'build_assets': WebpackBuildCommand,
        'watch': WebpackDevelopCommand,
    },
)

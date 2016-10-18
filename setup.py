from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, Extension, find_packages
import os
import sys


setup(
    name='camcap',
    version='dev',
    scripts=['scripts/camcap', 'scripts/camcap_engine', 'scripts/camcap_gui'],
    include_package_data=True,
    # ext_modules=[prosilica_module],
    packages=find_packages(exclude=['tests', 'scripts']),
    data_files=[(os.path.expanduser('~/.camerastream'),
                ['config/config.ini'])]
    )
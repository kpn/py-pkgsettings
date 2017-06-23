#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pkgversion import list_requirements, pep440_version, write_setup_py
from setuptools import find_packages

write_setup_py(
    name='pkgsettings',
    version=pep440_version(),
    description="Python package to ease the configuration of packages",
    long_description=open('README.rst').read(),
    author="Niels Lensink",
    author_email='niels.lenssink@kpn.com',
    url='https://github.com/kpn-digital/py-pkgsettings.git',
    install_requires=list_requirements('requirements/requirements-base.txt'),
    packages=find_packages(exclude=['tests*']),
    tests_require=['tox'],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ]
)

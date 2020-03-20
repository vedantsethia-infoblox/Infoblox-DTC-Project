#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('../README.md') as readme_file:
    readme = readme_file.read()


with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()



setup(
    name='DTC-RATIO_DYNAMIC',
    version='0.0.3',
    description="Dynamic Ratio Manipulation of DTC Pools",
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Vedant Sethia",
    author_email='vsethia@infoblox.com',
    url='https://github.com/vedantsethia-infoblox/Infoblox-DTC-Project',
    packages=[
        'project',
    ],
    package_dir={'project':
                 'firstsite'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache",
    zip_safe=False,
    keywords='DTC',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)

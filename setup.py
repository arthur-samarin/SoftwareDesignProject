#!/usr/bin/env python3
import setuptools

setuptools.setup(
    name="SoftwareDesignProject",
    version="1.0.0",
    description="Project for Software Design course",
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'SQLAlchemy==1.2.14'
    ],
    tests_require=[

    ],
    entry_points={
        'console_scripts': [
            'sdproject = app.main:main'
        ]
    }
)

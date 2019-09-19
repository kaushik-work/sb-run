#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
from datetime import datetime
from setuptools import setup, find_packages

current_path = pathlib.Path(__file__).parent

name = 'sb-run'
ver_path = pathlib.Path(current_path, "sbrun", "version.py")
_ver = {}
exec(ver_path.open("r").read(), _ver)
version = _ver["__version__"]
now = datetime.utcnow()
desc_path = pathlib.Path(current_path, "Readme.md")
long_description = desc_path.open("r").read()

setup(
    name=name,
    version=version,
    packages=find_packages(),
    platforms=['POSIX', 'MacOS', 'Windows'],
    python_requires='>=3.7.0',
    install_requires=[
        "sevenbridges-python"
    ],
    entry_points={
        'console_scripts': [
            'sbpush = sbrun.__main__:push',
            'sbrun =  sbrun.__main__:run'
        ],
    },

    author='Seven Bridges',
    maintainer='Seven Bridges',
    maintainer_email='kaushik.ghose@sbgenomics.com',
    author_email='kaushik.ghose@sbgenomics.com',
    description='Command line tool to upload CWL documents to SB powered platforms and run them',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    license='Copyright (c) {} Seven Bridges'.format(now.year),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords='seven bridges cwl common workflow language'
)

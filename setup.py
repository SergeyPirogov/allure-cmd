from setuptools import setup, find_packages
from io import open
from os import path

import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
# README = (HERE / "README.md").read_text()

# automatically captured required modules for install_requires in requirements.txt
with open(path.join(HERE, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if ('git+' not in x) and (
    not x.startswith('#')) and (not x.startswith('-'))]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs \
                    if 'git+' not in x]
setup(
    name='allure-cmd',
    description='A simple commandline app for Allure report generation',
    version='0.0.5',
    packages=find_packages(),  # list of all packages
    install_requires=install_requires,
    python_requires='>=3.6',  # any python greater than 2.7
    entry_points='''
        [console_scripts]
        allure=allure.__main__:main
    ''',
    author="Sergey Pirogov",
    keyword="allure report generator",
    long_description="",
    long_description_content_type="text/markdown",
    license='MIT',
    url='https://github.com/SergeyPirogov/allure-cmd',
    download_url='',
    dependency_links=dependency_links,
    author_email='semen4ik20@gmail.com',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ]
)

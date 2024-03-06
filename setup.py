from setuptools import setup, find_packages

setup(
    name='battleship',
    version='0.1',
    packages=find_packages(include=['pocs', 'Battleship', 'battleship']),
    # include or exclude patterns as necessary
)
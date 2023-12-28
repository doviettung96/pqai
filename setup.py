from setuptools import setup, find_packages

setup(
    name='pqai',
    version='1.0.0',
    description='Retrieve patent data from https://search.projectpq.ai/',
    author='Ace',
    author_email='ace@cinnamon.is',
    # url="",
    packages=find_packages(exclude=["plugins*", "*tests*"]),
    install_requires=[
        # List your module's dependencies here
    ],
)
from setuptools import setup, find_packages

setup(
    name="myservice",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.0"
    ],
    extras_require={"dev":["pytest"]}
)
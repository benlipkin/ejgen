from setuptools import find_packages, setup

with open("requirements.txt") as reqs_file:
    requirements = reqs_file.read().split("\n")

setup(
    name="model",
    packages=find_packages(where="model"),
    install_requires=requirements,
    python_requires=">=3.10",
)

from setuptools import setup, find_packages

setup(
    name="stress_relationships",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    include_package_data=True,
    description="A Python library for stress relationships.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cjmiddleton225/stress_relationships",  # update as needed
    author="Chris Middleton",  # update as needed
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)

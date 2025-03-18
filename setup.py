from setuptools import setup, find_packages

setup(
    name="asterrdetection",
    version="0.2",
    description="A package for finding the list of errors in a code compared to the expected code",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Badmavasan KIROUCHENASSAMY",
    author_email="badmavasan.kirouchenassamy@lip6.fr",
    url="https://github.com/Badmavasan/ast-error-detection",
    packages=find_packages(),
    install_requires=[
        "graphviz",
        "numpy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

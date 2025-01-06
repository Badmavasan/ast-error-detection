from setuptools import setup, find_packages

setup(
    name="ast-error-detection",
    version="0.1.0",
    description="A package for finding the list of errors in a code compared to the expected code",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Badmavasan KIROUCHENASSAMY",
    author_email="badmavasan.kirouchenassamy@lip6.fr",
    url="https://github.com/Badmavasan/ast-error-detection",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Commercial Licensing": "mailto:badmavasan.kirouchenassamy@lip6.fr",
    },
    python_requires=">=3.6",
)

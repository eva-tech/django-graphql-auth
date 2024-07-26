#!/usr/bin/env python

import io
import os
import re
from collections import OrderedDict

from setuptools import find_packages, setup


def get_version(package):
    with io.open(os.path.join(package, "__init__.py")) as f:
        pattern = r'^__version__ = [\'"]([^\'"]*)[\'"]'
        return re.search(pattern, f.read(), re.MULTILINE).group(1)


tests_require = [
    "pytest>=8.3.1",
    "pytest-cov>=5.0.0",
    "pytest-django>=4.8.0",
    "coveralls",
]

dev_requires = ["black==24.4.2", "flake8==7.1.0"] + tests_require

setup(
    name="django-graphql-auth",
    version=get_version("graphql_auth"),
    license="MIT",
    description="Graphql and relay authentication with Graphene for Django.",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    author="pedrobern",
    author_email="pedrobermoreira@gmail.com",
    maintainer="pedrobern",
    url="https://github.com/PedroBern/django-graphql-auth",
    project_urls=OrderedDict(
        (
            ("Documentation", "https://django-graphql-auth.readthedocs.io/en/latest/"),
            ("Issues", "https://github.com/PedroBern/django-graphql-auth/issues"),
        )
    ),
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "Django>=3,<4",
        "django-filter>=2.4.0",
        "django-graphql-jwt>=0.3.1",
        "graphene_django>=2.15.0,<3",
        "graphene>=2.1.9,<3",
    ],
    tests_require=tests_require,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
    ],
    keywords="api graphql rest relay graphene auth",
    zip_safe=False,
    include_package_data=True,
    extras_require={"test": tests_require, "dev": dev_requires},
)

"""Package setup."""

import setuptools

description = "A modern Python web framework filled with asynchronous salsa."

with open("README.md", "r") as readme:
    long_description = readme.read()

GITHUB = "https://github.com/bocadilloproject/bocadillo"
DOCS = "https://bocadilloproject.github.io"
CHANGELOG = f"{GITHUB}/blob/master/CHANGELOG.md"

setuptools.setup(
    name="bocadillo",
    version="0.13.1",
    author="Florimond Manca",
    author_email="florimond.manca@gmail.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["bocadillo"],
    package_data={"bocadillo": ["assets/*"]},
    install_requires=[
        "starlette>=0.11, <0.12",
        "uvicorn>=0.5.1, <0.6",
        "jinja2>=2.10",
        "whitenoise",
        "requests",
        "parse",
        "python-multipart",
        "websockets>=6.0",
        "aiodine>=1.2.5, <2.0",
    ],
    extras_require={"files": ["aiofiles"], "sessions": ["itsdangerous"]},
    python_requires=">=3.6",
    url=DOCS,
    project_urls={
        "Source": GITHUB,
        "Documentation": DOCS,
        "Changelog": CHANGELOG,
    },
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)

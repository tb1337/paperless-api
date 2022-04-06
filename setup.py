import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pypaperless",
    version="0.0.7",
    author="tbsch",
    author_email="info@tbsch.de",
    description="A small API wrapper for paperless-ngx dms.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/grdn1337/paperless-api",
    project_urls={
        "Bug Tracker": "https://github.com/grdn1337/paperless-api/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["pypaperless"],
    python_requires=">=3.6",
)

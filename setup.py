from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pypaperless",
    version="1.0.0",
    description="A small API wrapper for the paperless-ngx dms.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="tb1337",
    author_email="info@tbsch.de",
    url="https://github.com/tb1337/paperless-api",
    project_urls={
        "Source": "https://github.com/tb1337/paperless-api/",
        "Bug Tracker": "https://github.com/tb1337/paperless-api/issues",
    },
    install_requires=[
        "requests>=2.30.0",
        "urllib3>=2.0.0",
    ],
    packages=["pypaperless"],
    license="MIT",
    python_requires=">=3.9",
)

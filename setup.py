import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="UiL Django Core",
    version="1.0.0-rc1",
    author="UiL OTS Labs",
    author_email="labman.gw@uu.nl",
    description="A shared code library for UiL OTS Django projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UiL-OTS-labs/django-shared-core",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django :: 2.0",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)


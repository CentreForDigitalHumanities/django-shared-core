import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CDH Django Core",
    version="3.0.2",
    author="Humanities IT Portal development, ILS Labs",
    author_email="portaldev.gw@uu.nl, labbeheer.gw@uu.nl",
    description="A shared code library for Hum-IT & ILS Labs Django projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DH-IT-Portal-Development/django-shared-core",
    packages=setuptools.find_packages(),
    license_files=('LICENSE',),
    install_requires=[
        'django>=3.2',
        'pyscss',
        'lesscpy',
        'closure',
        'vbuild',
        'requests',
        'PyJWT',
        'djangorestframework',
        'python-magic',
        'django-filter',
        'Deprecated',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)

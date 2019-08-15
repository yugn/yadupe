import os.path
from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

setup(
    name="yadupe",
    version="1.0.0",
    description="Recursively scan one or more given directories for duplicate files.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/yugn/yadupe",
    author="yugn",
    author_email="cbznysrnpu@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows"
    ],
    packages=['yadupe'],
    install_requires=["tqdm"],
    entry_points={
        "console_scripts": [
            "yadupe=yadupe.__main__:main",
        ]
    },
)
import os
from setuptools import setup, find_packages

# Read version from version.py
version = {}
with open(os.path.join("src", "version.py")) as f:
    exec(f.read(), version)

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

sample_files = package_files('samples')

setup(
    name="msv",
    version=version['__version__'],
    packages=['src'],  # Explicitly declare the package
    package_data={
        'src': sample_files,
    },
    include_package_data=True,
    install_requires=[
        "pandas>=2.0.0",
        "openpyxl>=3.0.0",
        "openai>=1.0.0",
        "tomli>=2.0.1",
        "python-dotenv>=1.0.0"
    ],
    entry_points={
        'console_scripts': [
            'msv=src.main:main',
        ],
    },
    author="Vishal Gandhi",
    author_email="igandhivishal@gmail.com",
    description="A powerful CLI tool for merging and transforming CSV/XLSX files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/stackblitz/msv",
    keywords="csv xlsx data merge transform cli",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7"
)
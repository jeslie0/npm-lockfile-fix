from setuptools import setup, find_packages

setup(
    name = "npm-lockfile-fix",
    version = "0.1.0",
    author = "James Leslie",
    author_email = "jamesleslie@posteo.net",
    description = " A tool to add missing resolved and integrity fields to a npm package lockfile.",
    url = "https://github.com/jeslie0/npm-lockfile-fix",
    packages = find_packages(),
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'npm-lockfile-fix=src.__main__:main',
        ],
    },
    install_requires=[
        'requests',
    ]
)

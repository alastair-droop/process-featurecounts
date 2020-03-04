from setuptools import setup, find_packages
import os.path

# Get the version:
version = {}
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'prfeaturecounts', 'version.py')) as f: exec(f.read(), version)

setup(
    name = 'prfeaturecounts',
    version = version['__version__'],
    description = 'Command line script to simplify featureCounts output',
    author = 'Alastair Droop',
    author_email = 'alastair.droop@gmail.com',
    url = 'https://github.com/alastair.droop/process-featurecounts',
    classifiers = [
        'Programming Language :: Python :: 3'
    ],
    packages = find_packages(),
    python_requires = '>=3',
    entry_points = {
        'console_scripts': [
            'process-featurecounts=prfeaturecounts.scripts:main'
        ]
    }
)

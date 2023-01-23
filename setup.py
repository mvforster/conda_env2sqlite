from setuptools import setup, find_packages

VERSION = '1.0.0'
DESCRIPTION = 'A package to insert the details of Anaconda/Miniconda environments into an SQLite3 database'
LONG_DESCRIPTION = '''This package works in tandem with a set of BASH scripts that will cycle though
    the Anaconda/miniconda environments accessible to your use to export either a .txt or .yml ourline of the 
    environment. The package will take these text files as imput and process them for insertion of the details 
    of each python package into an SQLite3 database. The database will also include a copy of the imput file, which 
    can be used to recreate the conda environment in the event the environment is corrupted.'''

# Setting up
setup(
    name="conda_env2sqlite",
    version=VERSION,
    author="Matthieu Vizuete-Forster",
    author_email="<matthieu.vizueteforster@genimicsengland.co.uk>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['PyYaml'],
    keywords=['python','Anaconda', 'Miniconda', 'SQLite'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

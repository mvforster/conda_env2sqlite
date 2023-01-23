# Conda_env2SQLite

A Package for creating an SQLite3 database of python packages contained in a set of Anaconda and Miniconda environment YAML files or text files. The package will require that the text or YAML files to be created separately, this can be acheived with one of the follwing BASH scripts:

```bash
. $CONDA_BASE_ENV_PATH

declare -a envArray=($(conda env list | cut -d' ' -f1))

for e in "${envArray[@]}";
do
    # echo "${a}"
    if [ "${e}" = "#" ]; then
        continue
    else
    conda env export -n "${e}" > "${e}".yml
    fi
done
```

```bash
. $CONDA_BASE_ENV_PATH 

declare -a envArray=($(conda env list | cut -d' ' -f1))

for e in "${envArray[@]}";
do
    #echo $a
    if ["${e}" == "#"]; then
        continue
    else
        conda list -n "${e}" --export > "${e}".txt
    fi
done
```

The package will cycle through the produced files, extract the package names and versions and insert then into a relational database. The package will check for duplicate entries ensuring that all package and environment relationships are recorded. The database will also retain a copy of the processed file definning each conda environment. This allows the database to act as a back up for your conda environments. The recovered file can be used to rebuild a lost environemnt with the command:

```bash
conda env create --file <filename>.yml
```

or

```bash
conda env create --file <filename>.txt
```

## Authors

- [@mvforster](https://github.com/mvforster/conda_env2sqlite)

## Installation

Install my-project with pip

```bash
  pip install conda_env2sqlite
```

## Requirements

* PyYAML

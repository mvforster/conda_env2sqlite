#!/pgen_int_work/BRS/matvf/my_envs/mvf_test_env/bin/python
"""
Programme:  CondaEnv2SQLite
File:       conda_env2sqlite.py
Version:    Alpha_0.7
Date:       2021-08-04
Function:   Extracts information from Conda text or YAML files and inserts
            into an SQLite database
Copyright:  (c) Matthieu Vizuete-Forster, GEL, 2021
Author:     Matthieu Vizuete-Forster
Address:    Genomics England
            Queen Mary University of London
            Dawson Hall, Charterhouse Square
            London, EC1M 6BQ
--------------------------------------------------------------------------
Released under GPL v3.0 licence
--------------------------------------------------------------------------
Description:
============
The script is designed to:
    - search for text and yaml files within a directory
    - parse these Conda Environment Definition files
    - extract the relevant information and store these in an SQLite 
    database
    - convert the processed file into a format that can be stored in the 
    database
    - multiple entries for the same environment are possible as the 
    database is designed to allow some changes to be tracked, this is not
    full versioning of the environments but it allows a form of "recovery"
If the database is non existant the script will create the database file.
--------------------------------------------------------------------------
Usage:
======
The database name is currently hard-coded into the script, this may need 
to change in order to ensure that the same database is always used.
The script will search for the Conda Definition Files.
The script requires a username to be provided even for publically 
available environments. This is because there may be a way to leverage 
the database for a customer-facing tool with restricted access to 
"private" environments
--------------------------------------------------------------------------
Revision History:
=================
A_0.1   04.08.21    Alpha   By: MVF Comment: Defined funcitons to parse 
                                            text files, create database & 
                                            populate with data from file
A_0.2   05.08.21    Alpha   By: MVF Comment: Dropped the use of Pandas as
                                            this created more overhead
A_0.3   06.08.21    Alpha   By: MVF Comment: Included function to parse
                                            YAML files, re-factored 
                                            database population function
                                            to push similar data from both 
                                            file types
A_0.4   10.08.21    Alpha   By: MVF Comment: Included funciton to convert
                                            file to binary format and push
                                            to blob within the database
A_0.5   17.08.21    Alpha   By: MVF Comment: Refactored main process to 
                                            search for all files in the 
                                            working directory
A_0.6   19.08.21    Alpha   By: MVF Comment: Corrected error in environment
                                            path extraction. included YAML 
                                            parameter for safe loading.
A_0.7   24.08.21    Alpha   By: MVF Comment: Script errored with empty files,
                                            this is possible with some 
                                            caracters, introcuded feature to
                                            handle these errors.
A_0.8   10.11.21    Alpha   By: MVF Comment: Fixed bug in the database creation
                                            process which caused all packages to
                                            be associated with all subsequently 
                                            processed environments
A_0.9   09.03.22    Alpha   By: MVF Comment: Introduced conditions to reduce
                                            redundancy in the database
B_0.10  06.09.22    Beta    By: MVF Comment: repaired bug leading to a single
                                            file being processed multiple times
                                            over. Included helper function to 
                                            check for miss-formatted yaml files.
                                            Split script into logical sections
B_0.11  20.01.23    Beta    By: MVF Comment: silencing the output from this script
                                            so that we have a better chance to 
                                            automate the build.
1.0     20.01.23    Release By: MVF Comment: converted to package
"""
# Standard Library imports
import glob
import os
import shutil
from datetime import date
# Package Imports
from src.file_funcs import prune_duplicate_files, move_processed_file
from src.process_funcs import populate_db

if __name__ == '__main__':
    # Define static parameters, the database name should not change
    # The username should change, a generic username would need to be chosen
    # for public Conda environments. 
    user = 'u.ser@domain.com'
    timestamp = date.today().isoformat()
    database = f'{timestamp}_conda_catalogue.db'

    # Search for files to be processed
    yaml_files = glob.glob('*.yml')
    text_files = glob.glob('*.txt')
    txt_files  = prune_duplicate_files(yaml_files, text_files)
    files = txt_files + yaml_files
    files.sort()

    # Process files and populate the database
    # Skip files that are empty, this is a real usecase as there are some conda 
    #  envs that have a broken definition
    for f in files:
        if os.path.getsize(f) == 0:
            continue
        else:
            populate_db(f, user, database)
            move_processed_file(f)

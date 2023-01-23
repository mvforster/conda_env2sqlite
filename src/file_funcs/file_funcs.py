import yaml
import itertools
import glob
import os
import shutil
import hashlib

def check_yaml(infile):
    with open(infile, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
            for k,v in data.items():
                if k != 'dependencies':
                    return False
        except yaml.YAMLError as exc:
            return(exc)
    

def find_conda_defs(path):
    """
    Helper function to located the files needed to be processed
    Input: path to directory containing the def files
    Output: list of files to pass to other functions
    """
    file_list = glob.glob(f'{os.chdir(path)}/*.yml')
    return file_list

def compare_file_lists(yml_list, txt_list):
    """
    Helper function to check that a yaml and text file for the same environment
        are not both processed. As yaml files are prefered for conda environment
        creatiom if both a txt and yml exist then a yml will be favoured
    Input: list of files generated from the glob built-in
    Output: list of common filenames
    """
    ymls = [f.split('.')[0] for f in yml_list]
    txts = [f.split('.')[0] for f in txt_list]
    filenames = [y for y in ymls if y in txts]
    return filenames

def prune_duplicate_files(yml_list, txt_list):
    """
    Helper function to remove txt files from the list of file to process. uses 
        compare_file_lists function to determins which files need to be excluded
    Input: list of files generated from the glob built-in
    Output: new list of text filenames to process
    """
    files_to_prune = compare_file_lists(yml_list, txt_list)
    new_text_list = [t for t in txt_list if t.split('.')[0] not in files_to_prune]
    return new_text_list

def move_processed_file(filename):
    """
    Moves a file to a subdirectory, calling this function at the end of 
        the database population function will remove processed files and 
        will helo to prevent duplications
    Input: str with the name of the file that is being process
    Output: None
    """
    cwd = os.getcwd()
    source = f'{cwd}/{filename}'
    dest_dir = f'{cwd}/processed'
    destination = f'{dest_dir}/{filename}'
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        shutil.move(source, destination)
    else:
        shutil.move(source, destination)

def parse_text(input_file):
    """
    Parse text file export for a conda environment
    Input: name of a *.txt conda definition file
    
    Output: tuple of values containing the environment name, 
        the path and a zipped list of each package row to be 
        inserted into the database
    """
    env      = ''
    env_path = ''
    pkg_name = []
    pkg_vs   = []
    ch       = []
    pip      = []

    pkg_row = []
    
    with open(input_file, 'r') as stream:
        p = stream.readline().split(' ')[-1].strip(':\n')
        env = str(p.split('/')[-1])
        env_path = str(p)
        for line in stream.readlines():
            if '#' in line:
                continue
            else:
                # Handle pip installed packages, 
                # these do not have a channel listed so channel will 
                # need to be set to 'pip'
                if len(line.split()) == 3:
                    pkg_name.append(line.split()[0])
                    pkg_vs.append(line.split()[1])
                    ch.append('pip')
                    pip.append("TRUE")
                elif len(line.split()) == 4:
                    pkg_name.append(line.split()[0])
                    pkg_vs.append(line.split()[1])
                    ch.append(line.split()[3])
                    pip.append("FALSE")

    pkg_row = list(zip(pkg_name, pkg_vs, ch, pip))

    return env, env_path, pkg_row


def parse_yaml(input_file):
    """
    Parse YAML file export for a conda environment
    Input: name of a *.yml conda definition file
    
    Output: list of tuples, containing the environment name, 
        the path and a zipped list of each package row to be 
        inserted into a database
    """
    env      = ''
    env_path = ''
    pkg_name = []
    pkg_vs   = []
    ch       = []
    pip      = []

    with open(input_file) as stream:
        data = yaml.load(stream, Loader=yaml.FullLoader)
       
        for key, values in data.items():
            # Check to see if the environment is a correctly formed env else skip
            if 'dependencies' in data:
                dependencies = data['dependencies']
            else:
                continue
            env = data['name']
            ch = data['channels']
            
            if 'prefix' in key:
                env_path = data['prefix']
            else:
                env_path = 'Public'
            for d in dependencies:
                if type(d) == dict:
                    pip_pkgs = d['pip']
                    for p in pip_pkgs:
                        pkg_name.append(p.split('==')[0])
                        pkg_vs.append(p.split('==')[1])
                        pip.append("TRUE")
                else:
                    # print(d.split('=')[0], d.split('=')[1])
                    pkg_name.append(d.split('=')[0])
                    pkg_vs.append(d.split('=')[1])
                    pip.append("FALSE")

    pkg_row = list(set(zip(pkg_name, pkg_vs, itertools.repeat(ch[0], len(pkg_name)), pip)))
    return env, env_path, pkg_row


def convert_file_to_binary(filename):
    """
    Converts the processed file into a byte object for insertion into the database
    
    Input: string variable for the name of the file that is to be converted
    
    Output: byte object 
    """
    with open(filename, 'rb') as data:
        file_blob = data.read()
    return file_blob


def hash_file(filename):
    """
    Calculates the md5 checksum of the input YAML file

    Input: string variable for the name of the file to be hashed

    Output: md5checksum for the file
    """
    hash_md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
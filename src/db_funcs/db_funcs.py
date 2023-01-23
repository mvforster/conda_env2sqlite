import sqlite3

def check_db_for_env(database, env_name):
    """
    Function used to ensure that duplicate entries are not entered into 
            the database.
    Inputs: the environment name parsed out of the definition file the 
            name of the database that is being searched
    
    Output: True if the query retuns an environment ID, False if no ID is 
            returned
    Note: not entirely sure how to implement this function, environments 
    need to be updatable but duplicate entries need to be prevented. may
    be best to 
    """
    conn = sqlite3.connect(database, timeout = 10)
    c = conn.cursor()
    sql = f"""
    SELECT env_id
    FROM env
    WHERE env_name = '{env_name}';
    """
    c.execute(sql)
    env_exists = c.fetchall()
    c.close()
    if len(env_exists) > 0:
        return True
    else:
        return False


def check_db_for_pkg_vs(database, pkg_name, vrs):
    """
    Function to verify whether an entry exists within the database, the
        goal of this is to ensure that there are no duplicate entries.
    Inputs: requires the name of the database that is being checked, the
        name and version of the package to be verified
    Output: will return True if the package and version combination is 
        present in the database. False if the entry has not been seen 
        before
    """
    conn = sqlite3.connect(database, timeout = 10)
    c = conn.cursor()
    sql = f"""
            SELECT 
                package, 
                version 
            FROM 
                pkg
            WHERE 
                package = '{pkg_name}' AND
                version = '{vrs}';
            """
    c.execute(sql)
    pkg_vs_exists = c.fetchall()
    c.close()
    if len(pkg_vs_exists) > 0:
        return True
    else:
        return False
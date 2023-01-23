import imp


import sqlite3
from file_funcs import check_yaml, parse_text, parse_yaml, hash_file, convert_file_to_binary
from db_funcs import check_db_for_pkg_vs

def populate_db(input_file, user, database):
    """
    Collect data from conda environment process them into objects to be inserted into 
    input: name of the file to be parsed and inserted into the database, 
        and the user name.
    
    output: populated database rows
    """
    user  = user
    envs  = set()
    paths = set()
    rtnd_val = []

    # check file extentions 
    if input_file.endswith('.txt'):
        rtnd_val = parse_text(input_file)
    elif input_file.endswith('.yml'):
        if not check_yaml(input_file):
            rtnd_val = parse_yaml(input_file)
    else:
        raise Exception('Incorrect file extention')

    envs.add(rtnd_val[0])
    paths.add(rtnd_val[1])
    rows = rtnd_val[2]
    file_blob = convert_file_to_binary(input_file)
    file_md5 = hash_file(input_file)

    # Create connection to database
    conn = sqlite3.connect(database, timeout = 10)

    c = conn.cursor()

    create_tables = """
    CREATE TABLE IF NOT EXISTS pkg(
    pkg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    package TEXT,
    version TEXT,
    channel TEXT,
    pip INT,
    UNIQUE(package, version, channel, pip)
    );

    CREATE TABLE IF NOT EXISTS env(
    env_id INTEGER PRIMARY KEY AUTOINCREMENT,
    env_name TEXT,
    env_path TEXT,
    usr_id INTEGER,
    file BLOB NOT NULL,
    hash TEXT UNIQUE,
    reg_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(usr_id) REFERENCES usr(usr_id)
    );

    CREATE TABLE IF NOT EXISTS usr(
    usr_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE 
    );

    CREATE TABLE IF NOT EXISTS pkg_env_link(
    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pkg_id INTEGER,
    env_id INTEGER,
    FOREIGN KEY(pkg_id) REFERENCES pkg(pkg_id),
    FOREIGN KEY(env_id) REFERENCES env(env_id)
    UNIQUE(pkg_id, env_id)
    );
    """

    c.executescript(create_tables)


    # Populate user table
    c.execute("""
    INSERT OR IGNORE INTO usr(username) VALUES (?);""",
    (user,))

    # Recover user ID to link the Envs list
    c.execute("""
    SELECT usr_id FROM usr WHERE username = ?;""",
    (user,))

    usr_id = c.fetchone()

    # Populate environments table
    c.execute("""
    INSERT or IGNORE INTO env(env_name, env_path, usr_id, file, hash) VALUES (?, ?, ?, ?, ?);""", 
    (list(envs)[0], list(paths)[0], usr_id[0], file_blob, file_md5))

    # Recover the environment ID to link through pkg_env_link table
    c.execute("""
    SELECT env_id FROM env WHERE env_name = ?;""",
    (list(envs)[0],))

    env_id = c.fetchone()

    # Populate the packages table
    for row in rows:
        # check if the packages are in the database
        if not check_db_for_pkg_vs(database, row[0], row[1]):
            c.execute("""
            INSERT or IGNORE INTO pkg(package, version, channel, pip) VALUES (?,?,?,?);
            """, row)

            c.execute("""
            SELECT pkg_id, package, version FROM pkg WHERE package = ? AND version = ?
            """, (row[0], row[1]))
            pkg_id = c.fetchone()

            c.execute("""
            INSERT INTO pkg_env_link(pkg_id, env_id) VALUES(?, ?);
            """, (pkg_id[0], env_id[0]))

        else:
            c.execute("""
            SELECT pkg_id FROM pkg WHERE package = ? AND version = ?""", (row[0], row[1]))
            pkg_id = c.fetchone()

            c.execute("""
            INSERT INTO pkg_env_link(pkg_id, env_id) VALUES(?, ?);""",
            (pkg_id[0], env_id[0]))

    conn.commit()
    c.close()
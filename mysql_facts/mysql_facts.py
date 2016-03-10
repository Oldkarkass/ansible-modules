#!/usr/bin/python

DOCUMENTATION = '''
---
module: mysql_facts
short_description: Extract details from a MySQL database.
description:
   - list user and host from a MySQL database.
   - list variables
   - list schemas
options:
    none

author: "OldKarkass"
extends_documentation_fragment: mysql
'''

EXAMPLES = """
# Gather MySQL facts
- mysql_facts:
"""

import json
import getpass
import tempfile
import re
import string

try:
    import MySQLdb
except ImportError:
    mysqldb_found = False
else:
    mysqldb_found = True

class InvalidPrivsError(Exception):
    pass

def users_get(cursor):
    cursor.execute("SELECT user,host FROM mysql.user")
    output = cursor.fetchall()
    results = []

    for line in output:
        results.append(dict(user=line[0] ,  host=line[1]) )

    return results

def variables_get(cursor):
    cursor.execute("SHOW variables")
    output = cursor.fetchall()
    results = []

    for line in output:
        results.append(dict(key=line[0],  value=line[1]) )

    return results

def schemas_get(cursor):
    cursor.execute("SHOW DATABASES")
    output = cursor.fetchall()
    results = []

    for line in output:
        results.append(dict(name=line[0]) )

    return results

# ===========================================
# Module execution.
#

def main():
    module = AnsibleModule(
        argument_spec = dict(
            login_user=dict(default=None),
            login_password=dict(default=None),
            login_host=dict(default="localhost"),
            login_port=dict(default=3306, type='int'),
            login_unix_socket=dict(default=None),
            config_file=dict(default="~/.my.cnf"),
            check_implicit_admin=dict(default=False, type='bool'),
            ssl_cert=dict(default=None),
            ssl_key=dict(default=None),
            ssl_ca=dict(default=None),
        ),
        supports_check_mode=True
    )
    login_user = module.params["login_user"]
    login_password = module.params["login_password"]
    config_file = module.params['config_file']
    ssl_cert = module.params["ssl_cert"]
    ssl_key = module.params["ssl_key"]
    ssl_ca = module.params["ssl_ca"]
    check_implicit_admin = module.params['check_implicit_admin']
    db = 'mysql'

    config_file = os.path.expanduser(os.path.expandvars(config_file))
    if not mysqldb_found:
        module.fail_json(msg="the python mysqldb module is required")

    cursor = None
    try:
        if check_implicit_admin:
            try:
                cursor = mysql_connect(module, 'root', '', config_file, ssl_cert, ssl_key, ssl_ca, db)
            except:
                pass

        if not cursor:
            cursor = mysql_connect(module, login_user, login_password, config_file, ssl_cert, ssl_key, ssl_ca, db)
    except Exception, e:
        module.fail_json(msg="unable to connect to database, check login_user and login_password are correct or %s has the credentials. Exception message: %s" % (config_file, e))


    results = { 'ansible_facts': {}  }
    results['ansible_facts']['mysql_user'] = users_get(cursor)
    results['ansible_facts']['mysql_variables'] = variables_get(cursor)
    results['ansible_facts']['mysql_schemas'] = schemas_get(cursor)

    module.exit_json(**results)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.database import *
from ansible.module_utils.mysql import *
if __name__ == '__main__':
    main()

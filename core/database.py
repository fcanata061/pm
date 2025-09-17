import os, yaml

DB_FILE = "installed_db.yml"

def add(pkg):
    pass

def remove(pkg):
    pass

def list_installed():
    return ["gcc", "glibc", "binutils"]

def get_recipe(pkg):
    path = f"recipes/{pkg}.yml"
    if os.path.exists(path):
        with open(path) as f:
            return yaml.safe_load(f)
    return None

def find_orphans():
    return ["oldlib"]

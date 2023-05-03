import json, os

with open(f"config{os.sep}config.json") as f:
    config = json.load(f)


"""Bot"""
token = config["token"]
sub   = config["sub_token"]

verified_roles = config["verify_roles"]
verified_servers = config["verify_servers"]


"""File PATHs"""
ROOT = os.curdir

FUNSHI = ROOT + os.sep + "funshi" + os.sep
FUNSHI_JSON = FUNSHI + "json" + os.sep + "funshi.json"

BACKUP = FUNSHI + os.sep + "backup" + os.sep
BACKUP_JSON = BACKUP + "backup.json"



cog_files = [
    f"cogs.{os.path.splitext(fp)[0]}" for fp in os.listdir(f"{os.curdir}{os.sep}cogs{os.sep}") if fp.endswith(".py")
]
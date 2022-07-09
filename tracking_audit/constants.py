import configparser
from pathlib import Path
import os
from datetime import datetime
import random

PARENT_DIR = Path().resolve()
# parse config file and make it available to the entire module
config = configparser.ConfigParser()
config.read(os.path.join(PARENT_DIR, "config.ini"))

# generate some path relevant constants from the config file
OUTPUT_PATH = config.get("output", "path")
PATH_TO_OPENWPM = config.get("openwpm", "path")

# output dir
OUTPUT_DIR = os.path.join(PARENT_DIR, "output")
if not os.path.isdir(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

# profiles sub dir
PROFILES_SUBDIR = os.path.join(PARENT_DIR, "resources", "profiles")
if not os.path.isdir(PROFILES_SUBDIR):
    os.mkdir(PROFILES_SUBDIR)

# default audit name
DEFAULT_AUDIT_NAME = "test_audit"

# Get request timeout
GET_REQUEST_TIMEOUT = 60

# Sleep time uniform min and max
SLEEP_TIME_UNIFORM_DIST_MIN = 6
SLEEP_TIME_UNIFORM_DIST_MAX = 60

# working hours
ACTIVE_STATUS_START = 8

ACTIVE_STATUS_STOP = 19

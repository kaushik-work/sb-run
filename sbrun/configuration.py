#  Copyright (c) 2019 Seven Bridges. See LICENSE

import os
from pathlib import Path as P

import logging
logger = logging.getLogger(__name__)


sbg_config_dir = P("sevenbridges", "sb-run")


# https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

xdg_config_dir = {
    "env": "XDG_CONFIG_HOME",
    "default": P(P.home(), ".config")
}

# There is a raging debate on this and people want to add a new field to the XDG spec
# Me, I think logs are user data ...
xdg_data_home = {
    "env": "XDG_DATA_HOME",
    "default": P(P.home(), ".local", "share")
}


class Configuration:
    def __init__(self):

        self.cfg_path = P(os.getenv(xdg_config_dir["env"], xdg_config_dir["default"]), sbg_config_dir)
        self.log_path = P(os.getenv(xdg_data_home["env"], xdg_data_home["default"]), sbg_config_dir, "logs")
        self.scratch_path = P(os.getenv(xdg_data_home["env"], xdg_data_home["default"]), sbg_config_dir, "scratch")

        if not self.log_path.exists():
            self.log_path.mkdir(parents=True)

        if not self.scratch_path.exists():
            self.scratch_path.mkdir(parents=True)

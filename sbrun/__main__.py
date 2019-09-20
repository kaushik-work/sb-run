#  Copyright (c) 2019 Seven Bridges. See LICENSE

import sys
import pathlib

from .configuration import Configuration

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError

from .pack import pack
from .push import push_to_sbpla
from .run import run_on_sbpla

import logging
logger = logging.getLogger()


fast_load = YAML(typ='safe')
sbg_cache_ext = ".sbpush.cache.yml"


def parse_args():

    if len(sys.argv) == 7:
        return {
            "cwl": sys.argv[1],
            "commit message": sys.argv[2],
            "profile": sys.argv[3],
            "user": sys.argv[4],
            "project": sys.argv[5],
            "app_id": sys.argv[6]
        }

    if len(sys.argv) == 3:
        return retrieve_cache(pathlib.Path(sys.argv[1]), commit_message=sys.argv[2])

    if len(sys.argv) == 2:
        return retrieve_cache(pathlib.Path(sys.argv[1]))

    return {}


def retrieve_cache(cwl: str, commit_message=None):
    config = Configuration()
    sbg_cache_file = config.scratch_path / \
                     pathlib.Path(*pathlib.Path(cwl).absolute().with_suffix(sbg_cache_ext).parts[1:])

    cache_data = {}
    if sbg_cache_file.exists():
        try:
            cache_data = fast_load.load(sbg_cache_file.open().read() or "")
        except (ParserError, ScannerError) as e:
            logger.error(f"Error loading SBG cache file {sbg_cache_file}")
    else:
        logger.error(f"No SBG cache file {sbg_cache_file}")

    if commit_message is not None:
        cache_data["commit message"] = commit_message

    return cache_data


def save_cache(cwl: str, cache_data):
    config = Configuration()
    sbg_cache_file = config.scratch_path / \
                     pathlib.Path(*pathlib.Path(cwl).absolute().with_suffix(sbg_cache_ext).parts[1:])

    if not sbg_cache_file.exists():
        sbg_cache_file.parent.mkdir(parents=True, exist_ok=True)

    fast_load.dump(cache_data, sbg_cache_file)


def push():
    args = parse_args()
    if "profile" not in args:
        print(
"""
sbpush <cwl> <commit message> <profile> <user> <project> <app_id>
sbpush <cwl> <commit message>
sbpush <cwl>
"""
        )
        sys.exit(1)

    cwl_dict = pack(pathlib.Path(args["cwl"]))
    push_to_sbpla(cwl_dict, commit_message=args["commit message"],
                  profile=args["profile"], user=args["user"],
                  project=args["project"], app_id=args["app_id"])
    save_cache(args["cwl"], args)


def run():
    args = parse_args()
    if "profile" not in args:
        print(
"""
sbrun <cwl> <profile> <user> <project> <appid>
sbrun <cwl>
"""
        )
        sys.exit(1)

    task = run_on_sbpla(profile=args["profile"], user=args["user"], project=args["project"],
                        app_id=args["app_id"],
                        old_task_id=args.get("old task id"))
    args["old task id"] = task.id
    save_cache(args["cwl"], args)

#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
from typing import Union

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError

import logging
logger = logging.getLogger(__name__)
logging.getLogger("sevenbridges.http.client").propagate = False
logging.getLogger("urllib3.connectionpool").propagate = False

fast_load = YAML(typ='safe')


def pack(path: pathlib.Path):
    """Load the YAML into a JSON.
        If any steps are linked (strings rather than dicts) insert them - recursively - into the JSON
        If any typedefs are $imports insert them
        If any javascript $import it and insert
        """
    cwl = load_yaml(path)
    pack_requirements(cwl, path)
    pack_steps(cwl, path)
    express_maps_as_lists(cwl)
    return cwl


def load_yaml(path):
    if path.exists():
        try:
            return fast_load.load(path.open("r").read())
        except (ParserError, ScannerError):
            pass


def list_as_map(node, key_field):
    if isinstance(node, dict):
        return node

    new_node = {}
    if isinstance(node, list):
        for n, _item in enumerate(node):
            if isinstance(_item, dict):
                key = _item.get(key_field)
                if key is not None:
                    new_node[key] = _item
                else:
                    # This is a problem
                    pass

    return new_node


def express_maps_as_lists(cwl: dict):
    cwl["inputs"] = map_as_list(cwl["inputs"], key_field="id", predicate_field="type")
    cwl["outputs"] = map_as_list(cwl["outputs"], key_field="id", predicate_field="type")
    if "steps" in cwl:
        cwl["steps"] = map_as_list(cwl["steps"], key_field="id", predicate_field=None)


# SBG PLA insists on lists ...
def map_as_list(node, key_field, predicate_field):
    if isinstance(node, list):
        return node

    new_node = []
    if isinstance(node, dict):
        for k, _item in node.items():
            if not isinstance(_item, dict):
                _item = {
                    key_field: k,
                    predicate_field: _item
                }
            if isinstance(_item, dict):
                if key_field not in _item:
                    _item[key_field] = k
            new_node += [_item]

    return new_node


# todo: we can refactor lib.resolve_file_path
def resolve_file_path(path, target_path):
    _path = pathlib.PurePosixPath(target_path)
    if not _path.is_absolute():
        base_path = path.parent
    else:
        base_path = "."
    _path = pathlib.Path(base_path / _path).resolve().absolute()
    return _path


def pack_steps(cwl: dict, path: pathlib.Path):
    steps = cwl.get("steps")
    if isinstance(steps, (dict, list)):
        for step_id, step in list_as_map(steps, key_field="id").items():
            if isinstance(step, dict):
                run = step.get("run")
                if isinstance(run, str):
                    step["run"] = pack(resolve_file_path(path, run))


def pack_requirements(cwl: dict, path: pathlib.Path):
    _req = cwl.get("requirements")
    if isinstance(_req, (dict, list)):
        for req_class, req in list_as_map(_req, key_field="class").items():
            if req_class == "SchemaDefRequirement":
                user_types = extract_schemadefs(req["types"], path)
                resolve_typedefs("inputs", cwl, user_types)
                resolve_typedefs("outputs", cwl, user_types)
                req["types"] = []  # wipe it
            if req_class == "InlineJavascriptRequirement":
                inline_js(req.get("expressionLib"), path)


def extract_schemadefs(field: dict, path: pathlib.Path):
    user_types = {}
    if isinstance(field, list):
        for n, sr in enumerate(field):
            if isinstance(sr, dict):
                if list(sr.keys()) == ["$import"]:
                    _name_prefix = sr["$import"]
                    these_type_defs = load_yaml(resolve_file_path(path, sr["$import"]))
                    if not isinstance(these_type_defs, list):
                        these_type_defs = [these_type_defs]

                    for type_name, _type in list_as_map(these_type_defs, key_field="name").items():
                        _name = _name_prefix + "#" + _type["name"]
                        user_types[_name] = _type
    return user_types


def resolve_typedefs(port: str, cwl: dict, user_types: dict):
    if port not in ["inputs", "outputs"]:
        raise RuntimeError()

    if port not in cwl:
        return

    cwl[port] = list_as_map(cwl.get(port), key_field="id")

    for inp_id, inp in cwl[port].items():
        if isinstance(inp, list):
            cwl[port][inp_id] = {
                "id": inp_id,
                "type": [resolve_type(this_inp, user_types) for this_inp in inp]
            }
        elif isinstance(inp, str):
            cwl[port][inp_id] = {
                "id": inp_id,
                "type": resolve_type(inp, user_types)
            }
        else:
            cwl[port][inp_id] = resolve_type(inp, user_types)


primitive_types = tuple(
    sy + ext
    for sy in (
        "null",
        "boolean",
        "int",
        "long",
        "float",
        "double",
        "string"
        "File",
        "Directory"
    )
    for ext in ["", "[]", "?", "[]?"]
)


# Only needed to de-sugar mapping
def process_input_type(inp: Union[str, list, dict], user_types: dict):

    if isinstance(inp, str):
        if inp in primitive_types:
            return inp

        inp = {
            "type": inp
        }

    _ty = inp.get("type")
    if isinstance(_ty, str):
        inp["type"] = resolve_type(_ty, user_types)
    return inp


def resolve_type(_type: Union[str, list, dict], user_types: dict):
    if _type is None:
        return None
    elif isinstance(_type, list):
        return [resolve_type(_t, user_types) for _t in _type]
    elif isinstance(_type, dict):
        _ty = _type.get("type")
        if _ty is not None:
            _type["type"] = resolve_type(_ty, user_types)
            return _type
    elif _type in primitive_types:
        return _type
    else:
        if _type.endswith("?"):
            return [
                    "null",
                    resolve_type(_type[:-1], user_types)
                ]
        elif _type.endswith("[]"):
            return {
                "type": "array",
                "items": resolve_type(_type[:-2], user_types)
            }
        else:
            if _type in user_types:
                return user_types[_type]
            else:
                return _type


def inline_schemadefs(field: dict, path: pathlib.Path):
    if isinstance(field, list):
        for n, sr in enumerate(field):
            if isinstance(sr, dict):
                if list(sr.keys()) == ["$import"]:
                    _name_prefix = sr["$import"]
                    field[n] = load_yaml(resolve_file_path(path, sr["$import"]))
                    field[n]["name"] = _name_prefix + "#" + field[n]["name"]


def inline_js(field: dict, path: pathlib.Path):
    if isinstance(field, list):
        for n, sr in enumerate(field):
            if isinstance(sr, dict):
                if list(sr.keys()) == ["$include"]:
                    field[n] = load_yaml(resolve_file_path(path, sr["$include"]))

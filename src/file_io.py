import struct
import pathlib
import json


def load_from_file():
    with open("challenge.bin", "rb") as f:
        byte_program = f.read()
        return tuple(map(lambda x:x[0], struct.iter_unpack("<H", byte_program)))
    return None

def load_state(name):
    path = __get_state_path(name)
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

def save_state(state, name):
    json.dump(state, f, indent=2)

def __get_state_path(name):
    return "states" / pathlib.Path(name+".json")

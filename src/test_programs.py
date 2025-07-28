import unittest
import itertools
import struct
import pathlib
import json
from machine import *

class ProgramTest(unittest.TestCase):

    def __load_from_file(self):
        with open("challenge.bin", "rb") as f:
            byte_program = f.read()
            return tuple(map(lambda x:x[0], struct.iter_unpack("<H", byte_program)))
        return None

    def __assertOrSaveState(self, m, name : str):
        path = "states" / pathlib.Path(name+".json")
        if path.exists():
            with open(path) as f:
                current_state = m.get_state()
                expected_state = json.load(f)
                self.assertDictEqual(current_state, expected_state)
        else:
            with open(path, "w") as f:
                state = m.get_state()
                json.dump(state, f, indent=2)

    def test_ex1(self):
        m = Machine()
        m.load([9,32768,32769,4,19,32768])
        m.registers[1].set(ord("a"))
        m.run()
        self.assertEqual(m.pc, 6)
        self.assertEqual(m.term_out, "e")

    def test_init(self):
        m = Machine()
        m.load(self.__load_from_file())
        m.set_term_break(r"website:.*\n")
        m.run()
        self.__assertOrSaveState(m, "after_init")
        print(m.term_out)
        

if __name__ == '__main__':
    unittest.main()
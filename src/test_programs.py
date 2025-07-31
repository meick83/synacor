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
        expected_state = self.__load_state(name)
        if expected_state is not None:
            current_state = m.get_state()
            self.assertDictEqual(current_state, expected_state)
        else:
            path = self.__get_state_path(name)
            with open(path, "w") as f:
                state = m.get_state()
                json.dump(state, f, indent=2)

    def __load_state(self, name):
        path = self.__get_state_path(name)
        if not path.exists():
            return None
        with open(path) as f:
            return json.load(f)

    def __get_state_path(self, name):
        return "states" / pathlib.Path(name+".json")

    def test_ex1(self):
        m = Machine()
        m.load([9,32768,32769,4,19,32768])
        m.registers[1].set(ord("a"))
        m.run()
        self.assertEqual(m.pc, 7)
        self.assertListEqual(m.term_out, ["e"])

    def test_init(self):
        m = Machine()
        m.load(self.__load_from_file())
        m.set_term_break(r"website:.*")
        m.run()
        self.__assertOrSaveState(m, "after_init")
        print("\n".join(m.term_out))

    def test_selftest(self):
        m = Machine()
        m.load(self.__load_from_file())
        m.load_state(self.__load_state("after_init"))
        m.set_term_break(r"The self-test completion code is")
        m.run()
        self.__assertOrSaveState(m, "after_selftest")
        print("\n".join(m.term_out))

    def test_take_tablet(self):
        m = Machine()
        m.load(self.__load_from_file())
        m.load_state(self.__load_state("after_selftest"))
        m.term_in = ["take tablet", "use tablet"]
        m.set_term_break("You find yourself writing .* on the tablet.")
        m.run()
        self.__assertOrSaveState(m, "after_tablet_use")
        print("\n".join(m.term_out))

        

if __name__ == '__main__':
    unittest.main()
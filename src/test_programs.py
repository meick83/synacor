import unittest
import itertools
import struct
from machine import *

class ProgramTest(unittest.TestCase):

    def test_ex1(self):
        m = Machine()
        m.load([9,32768,32769,4,19,32768])
        m.registers[1].set(ord("a"))
        m.run()
        self.assertEqual(m.pc, 6)
        self.assertEqual(m.term_out, "e")

    def test_bin(self):
        word_program = None
        with open("challenge.bin", "rb") as f:
            byte_program = f.read()
            word_program = tuple(map(lambda x:x[0], struct.iter_unpack("<H", byte_program)))
        m = Machine()
        m.load(word_program)
        m.run()
        

if __name__ == '__main__':
    unittest.main()
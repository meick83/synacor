import unittest
import itertools
from machine import *

class ProgramTest(unittest.TestCase):

    def test_ex1(self):
        m = Machine()
        m.load([9,32768,32769,4,19,32768])
        m.registers[1] = ord("a")
        m.run()
        self.assertEqual(m.pc, 6)
        self.assertEqual(m.term_out, "e")

    def test_bin(self):
        word_program = []
        with open("challenge.bin", "rb") as f:
            byte_program = f.read()
            for lb, hb in itertools.batched(byte_program, n=2):
                word_program.append((hb << 8) + lb)
        m = Machine()
        m.load(word_program)
        m.run()
        

if __name__ == '__main__':
    unittest.main()
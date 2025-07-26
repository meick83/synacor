import unittest
from machine import *

class ProgramTest(unittest.TestCase):

    def test_ex1(self):
        m = Machine()
        m.load([9,32768,32769,4,19,32768])
        m.registers[1] = ord("a")
        m.run()
        self.assertEqual(m.pc, 6)
        self.assertEqual(m.term_out, "e")

if __name__ == '__main__':
    unittest.main()
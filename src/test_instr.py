import unittest
from machine import *

class InstructionTest(unittest.TestCase):

    def test_add(self):
        m = Machine()
        m.load([9,32768,8,4,0])
        m.run()
        self.assertEqual(m.pc, 4)
        self.assertEqual(m.registers[0], 12)

    def test_halt(self):
        m = Machine()
        m.load([0])
        m.run()
        self.assertEqual(m.pc, 0)

    def test_noop(self):
        m = Machine()
        m.load([21,0])
        m.run()
        self.assertEqual(m.pc, 1)

    def test_out(self):
        m = Machine()
        m.load([19,ord("$"),0])
        m.run()
        self.assertEqual(m.pc, 2)
        self.assertEqual(m.term_out,"$")

if __name__ == '__main__':
    unittest.main()
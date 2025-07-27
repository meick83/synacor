import unittest
from machine import *

class InstructionTest(unittest.TestCase):

    def test_set(self):
        m = Machine()
        m.load([1, 32768, 1234])
        m.run()
        self.assertEqual(m.pc, 3)
        self.assertEqual(m.registers[0].get(), 1234)

    def test_eq(self):
        m = Machine()
        m.load([4,32768,1,1])
        m.run()
        self.assertEqual(m.pc, 4)
        self.assertEqual(m.registers[0].get(), 1)
        m = Machine()
        m.load([4,32768,1,0])
        m.run()
        self.assertEqual(m.pc, 4)
        self.assertEqual(m.registers[0].get(), 0)

    def test_jmp(self):
        m = Machine()
        m.load([6,10])
        m.run()
        self.assertEqual(m.pc, 10)

    def test_jt(self):
        m = Machine()
        m.load([7,0,10])
        m.run()
        self.assertEqual(m.pc, 3)
        m = Machine()
        m.load([7,1,10])
        m.run()
        self.assertEqual(m.pc, 10)

    def test_jf(self):
        m = Machine()
        m.load([8,1,10])
        m.run()
        self.assertEqual(m.pc, 3)
        m = Machine()
        m.load([8,0,10])
        m.run()
        self.assertEqual(m.pc, 10)

    def test_add(self):
        m = Machine()
        m.load([9,32768,8,4,0])
        m.run()
        self.assertEqual(m.pc, 4)
        self.assertEqual(m.registers[0].get(), 12)

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
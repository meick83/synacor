import unittest
from machine import *

class InstructionTest(unittest.TestCase):

    def test_set(self):
        m = Machine()
        m.load([1, 32768, 1234])
        m.run()
        self.assertEqual(m.pc, 3)
        self.assertEqual(m.registers[0].get(), 1234)

    def test_push(self):
        m = Machine()
        m.load([2, 1234])
        m.run()
        self.assertEqual(m.pc, 2)
        self.assertListEqual(m.stack,[1234])

    def test_pop(self):
        m = Machine()
        m.load([3, 32768])
        m.stack = [1234]
        m.run()
        self.assertEqual(m.pc, 2)
        self.assertListEqual(m.stack,[])
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

    def test_gt(self):
        m = Machine()
        m.load([5,32768,1,0])
        m.run()
        self.assertEqual(m.pc, 4)
        self.assertEqual(m.registers[0].get(), 1)
        m = Machine()
        m.load([5,32768,1,2])
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

    def test_mult(self):
        m = Machine()
        m.load([10,32768,3,4,0])
        m.run()
        self.assertEqual(m.pc, 4)
        self.assertEqual(m.registers[0].get(), 12)

    def test_mod(self):
        m = Machine()
        m.load([11,32768,4,3,0])
        m.run()
        self.assertEqual(m.pc, 4)
        self.assertEqual(m.registers[0].get(), 1)

    def test_and(self):
        m = Machine()
        m.load([12,32768,4,7,0])
        m.run()
        self.assertEqual(m.pc, 4)
        self.assertEqual(m.registers[0].get(), 4)

    def test_or(self):
        m = Machine()
        m.load([13,32768,4,3,0])
        m.run()
        self.assertEqual(m.pc, 4)
        self.assertEqual(m.registers[0].get(), 7)

    def test_not(self):
        m = Machine()
        m.load([14,32768,1,0])
        m.run()
        self.assertEqual(m.pc, 3)
        self.assertEqual(m.registers[0].get(), 0x7FFE)

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
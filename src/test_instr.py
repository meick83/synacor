import unittest
from machine import *

class InstructionTest(unittest.TestCase):

    def test_halt(self):
        m = Machine()
        m.load([0])
        m.run()
        self.assertEqual(m.pc, 0)

if __name__ == '__main__':
    unittest.main()
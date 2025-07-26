
class Machine:

    MEM_SIZE = 2**15
    MODULO = 32768

    def __init__(self):
        self.__reset()
        self.dispatch = [None]*22

    def load(self, data):
        lend = len(data)
        self.memory[0:lend] = data[:]

    def run(self):
        self.__reset()
        while True:
            opcode = self.memory[self.pc]
            if opcode == 0:
                return
            instr = self.dispatch[opcode]
            instr()

    def __reset(self):
        self.registers = [0]*8
        self.memory = [0]*Machine.MEM_SIZE
        self.stack = []
        self.pc = 0

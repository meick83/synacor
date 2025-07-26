
class Machine:

    MEM_SIZE = 2**15
    MODULO = 32768

    def __init__(self):
        self.__reset()
        self.memory = [0]*Machine.MEM_SIZE
        self.dispatch = [None]*22
        self.dispatch[19] = self.__out
        self.dispatch[21] = self.__noop

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
            self.pc += instr()

    def __reset(self):
        self.registers = [0]*8
        self.stack = []
        self.pc = 0
        self.term_out = ""

    def __out(self):
        ch = self.__literal_or_reg(1)
        self.term_out += chr(ch)
        return 2

    def __noop(self):
        return 1

    def __literal_or_reg(self, offset):
        arg = self.memory[self.pc + offset]
        if arg < 32768:
            return arg
        elif arg < 32776:
            return self.registers[arg - 32768]
        else:
            raise Exception(f"Invalid argument {arg}")

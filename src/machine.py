
class Machine:

    MEM_SIZE = 2**15
    MODULO = 32768

    def __init__(self):
        self.__reset()
        self.registers = [0]*8
        self.memory = [0]*Machine.MEM_SIZE
        self.dispatch = [None]*22
        self.dispatch[ 6] = self.__jmp
        self.dispatch[ 7] = self.__jt
        self.dispatch[ 8] = self.__jf
        self.dispatch[ 9] = self.__add
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
            if instr is None:
                raise Exception(f"unknown opcode {opcode}")
            self.pc += instr()

    def __reset(self):
        self.stack = []
        self.pc = 0
        self.term_out = ""

    def __jmp(self):
        a = self.__get_arg(1)
        return (a - self.pc)

    def __jt(self):
        a = self.__get_arg(1)
        b = self.__get_arg(2)
        if a != 0:
            return (b - self.pc)
        else:
            return 3

    def __jf(self):
        a = self.__get_arg(1)
        b = self.__get_arg(2)
        if a == 0:
            return (b - self.pc)
        else:
            return 3


    def __add(self):
        b = self.__get_arg(2)
        c = self.__get_arg(3)
        av = (b+c)%Machine.MODULO
        self.__store_arg(1, av)
        return 4
        

    def __out(self):
        ch = self.__get_arg(1)
        self.term_out += chr(ch)
        return 2

    def __noop(self):
        return 1

    def __get_arg(self, offset):
        arg = self.memory[self.pc + offset]
        if arg < 32768:
            return arg
        elif arg < 32776:
            return self.registers[arg - 32768]
        else:
            raise Exception(f"Invalid argument {arg}")

    def __store_arg(self, offset, value):
        arg = self.memory[self.pc + offset]
        if (32768 <= arg) and (arg < 32776):
            self.registers[arg - 32768] = value
        else:
            raise Exception(f"Invalid argument {arg}")
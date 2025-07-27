
from dataclasses import dataclass
import functools
import itertools

class InstructionDecoder:

    class Instr:
        def __init__(self, dispatch, *args):
            self.dispatch = dispatch
            self.args = args

    def __init__(self, dispatch_obj):
        self.dispatch_obj = dispatch_obj
        self.instr = [None]*22
        self.instr[ 0] = self.Instr(dispatch_obj.instr_exit)
        self.instr[ 1] = self.Instr(dispatch_obj.instr_set,  self.__O, self.__I)
        self.instr[ 2] = self.Instr(dispatch_obj.instr_push, self.__I)
        self.instr[ 3] = self.Instr(dispatch_obj.instr_pop,  self.__O)
        self.instr[ 4] = self.Instr(dispatch_obj.instr_eq ,  self.__O, self.__I, self.__I)
        self.instr[ 5] = self.Instr(dispatch_obj.instr_gt ,  self.__O, self.__I, self.__I)
        self.instr[ 6] = self.Instr(dispatch_obj.instr_jmp,  self.__I)
        self.instr[ 7] = self.Instr(dispatch_obj.instr_jt ,  self.__I, self.__I)
        self.instr[ 8] = self.Instr(dispatch_obj.instr_jf ,  self.__I, self.__I)
        self.instr[ 9] = self.Instr(dispatch_obj.instr_add,  self.__O, self.__I, self.__I)
        self.instr[10] = self.Instr(dispatch_obj.instr_mult, self.__O, self.__I, self.__I)
        self.instr[11] = self.Instr(dispatch_obj.instr_mod,  self.__O, self.__I, self.__I)
        self.instr[12] = self.Instr(dispatch_obj.instr_and,  self.__O, self.__I, self.__I)
        self.instr[13] = self.Instr(dispatch_obj.instr_or,   self.__O, self.__I, self.__I)
        self.instr[14] = self.Instr(dispatch_obj.instr_not,  self.__O, self.__I)
        self.instr[19] = self.Instr(dispatch_obj.instr_out,  self.__I)
        self.instr[21] = self.Instr(dispatch_obj.instr_noop)

    def decode(self, mem, pos):
        opcode = mem[pos]
        instr = self.instr[opcode]
        if instr is None:
            raise Exception(f"unknonwn opcode {opcode}")
        args = tuple(
            map(
                lambda f, v: f(v),
                instr.args,
                mem[pos+1:]
            )
        )

        return instr.dispatch, pos+len(args)+1, args

    def __O(self, arg):
        if (32768 <= arg) and (arg < 32776):
            return self.__get_register(arg - 32768)
        else:
            raise Exception(f"Invalid argument {arg}")

    def __I(self, arg):
        if arg < 32768:
            return self.__get_literal(arg)
        elif arg < 32776:
            return self.__get_register(arg - 32768)
        else:
            raise Exception(f"Invalid argument {arg}")

    @functools.cache
    def __get_literal(self, v):
        return self.dispatch_obj.get_literal(v)

    @functools.cache
    def __get_register(self, ix):
        return self.dispatch_obj.get_register(ix)



class Machine:

    MEM_SIZE = 2**15
    MODULO = 32768

    class Register:
        def __init__(self, ix):
            self.__ix = ix
            self.__value = 0
        def set(self, v):
            self.__value = v
        def get(self):
            return self.__value

    class Literal:
        def __init__(self, v):
            self.__value = v
        def get(self):
            return self.__value


    def __init__(self):
        self.registers = list(map(self.Register,range(8)))
        self.memory = [0]*Machine.MEM_SIZE
        self.stack = []
        self.pc = 0
        self.term_out = ""

        self.instr_exit = None
        self.get_literal = Machine.Literal
        self.get_register = self.registers.__getitem__
        self.decoder = InstructionDecoder(self)

    def load(self, data):
        lend = len(data)
        self.memory[0:lend] = data[:]

    def run(self):
        while True:
            dispatch, self.next_pc, args = self.decoder.decode(self.memory, self.pc)
            if dispatch is None:
                return
            dispatch(*args)
            self.pc = self.next_pc

    def instr_set(self, a, b):
        a.set(b.get())

    def instr_push(self, a):
        self.stack.append(a.get())

    def instr_pop(self, a):
        a.set(self.stack.pop())

    def instr_eq(self, a, b, c):
        if b.get() == c.get():
            a.set(1)
        else:
            a.set(0)

    def instr_gt(self, a, b, c):
        if b.get() > c.get():
            a.set(1)
        else:
            a.set(0)

    def instr_jmp(self, a):
        self.next_pc = a.get()

    def instr_jt(self, a, b):
        if a.get() != 0:
            self.next_pc = b.get()

    def instr_jf(self, a, b):
        if a.get() == 0:
            self.next_pc = b.get()


    def instr_add(self, a, b, c):
        av = (b.get()+c.get())%Machine.MODULO
        a.set(av)

    def instr_mult(self, a, b, c):
        av = (b.get()*c.get())%Machine.MODULO
        a.set(av)

    def instr_mod(self, a, b, c):
        av = b.get()%c.get()
        a.set(av)

    def instr_and(self, a, b, c):
        av = b.get()&c.get()
        a.set(av)
    
    def instr_or(self, a, b, c):
        av = b.get()|c.get()
        a.set(av)

    def instr_not(self, a, b):
        av = ~b.get()&0x7FFF
        a.set(av)
        

    def instr_out(self, a):
        self.term_out += chr(a.get())

    def instr_noop(self):
        pass

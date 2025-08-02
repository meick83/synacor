
from dataclasses import dataclass
import functools
import itertools
import re

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
        self.instr[15] = self.Instr(dispatch_obj.instr_rmem, self.__O, self.__I)
        self.instr[16] = self.Instr(dispatch_obj.instr_wmem, self.__I, self.__I)
        self.instr[17] = self.Instr(dispatch_obj.instr_call, self.__I)
        self.instr[18] = self.Instr(dispatch_obj.instr_ret)
        self.instr[19] = self.Instr(dispatch_obj.instr_out,  self.__I)
        self.instr[20] = self.Instr(dispatch_obj.instr_in,   self.__O)
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

        def get_state(self):
            return {"value" : self.__value}

        def load_state(self, src):
            self.__value = src["value"]

    class Literal:
        def __init__(self, v):
            self.__value = v
        def get(self):
            return self.__value


    def __init__(self):
        self.registers = list(map(self.Register,range(8)))
        self.memory = [0]*Machine.MEM_SIZE
        self.mem_low = Machine.MEM_SIZE
        self.mem_high = 0
        self.stack = []
        self.pc = 0
        self.term_out = [""]
        self.term_in = []
        self.instruction_cache = {}
        self.instruction_cache_limit = 0

        self.term_break : re.Pattern = None

        self.__running = False

        self.get_literal = Machine.Literal
        self.get_register = self.registers.__getitem__
        self.decoder = InstructionDecoder(self)

    def load(self, data):
        lend = len(data)
        self.memory[0:lend] = data[:]

    def get_state(self):
        state = {
            "registers" : list(map(self.Register.get_state, self.registers)),
            "pc" : self.pc,
            "stack" : self.stack,
            "mem_low" : self.mem_low,
            "mem_high" : self.mem_high,
            "memory" : self.memory[self.mem_low:self.mem_high+1],
            "term_out" : self.term_out
        }
        return state

    def load_state(self, state):
        for r,rs in zip(self.registers, state["registers"]):
            r.load_state(rs)
        self.pc = state["pc"]
        self.stack = state["stack"]
        self.mem_low = state["mem_low"]
        self.mem_high = state["mem_high"]
        if self.mem_low <= self.mem_high:
            smem = state["memory"]
            if len(smem)!=(self.mem_high - self.mem_low + 1):
                raise Exception("memory has invalid size")
            self.memory[self.mem_low:self.mem_high+1] = smem

    def set_term_break(self, regex : str):
        if regex is not None:
            self.term_break = re.compile(regex)
        else:
            self.term_break = None

    def run(self):
        self.__running = True
        while self.__running:
            dispatch, self.next_pc, args = self.__decode_next()
            dispatch(*args)
            self.pc = self.next_pc

    def __decode_next(self):
        cached = self.instruction_cache.get(self.pc)
        if cached is not None:
            return cached
        dispatch, next_pc, args = self.decoder.decode(self.memory, self.pc)
        self.instruction_cache[self.pc] = (dispatch, next_pc, args)
        if next_pc > self.instruction_cache_limit:
            self.instruction_cache_limit = next_pc
        return dispatch, next_pc, args

    def instr_exit(self):
        self.__running = False

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

    def instr_rmem(self, a, b):
        a.set(self.memory[b.get()])

    def instr_wmem(self, a, b):
        addr = a.get()
        self.memory[addr] = b.get()
        if addr < self.mem_low:
            self.mem_low = addr
        if addr > self.mem_high:
            self.mem_high = addr
        if addr < self.instruction_cache_limit:
            for i in range(0,4):
                if addr - i in self.instruction_cache:
                    del self.instruction_cache[addr - i]
                    break

    def instr_call(self, a):
        self.stack.append(self.next_pc)
        self.next_pc = a.get()

    def instr_ret(self):
        self.next_pc = self.stack.pop()

    def instr_out(self, a):
        ch = chr(a.get())
        if ch != '\n':
            self.term_out[-1] += ch
            return

        self.term_out.append("")
        
        if self.term_break is None:
            return
        m = self.term_break.search(self.term_out[-2])
        if m:
            self.__running = False

    def instr_in(self, a):
        if len(self.term_in) == 0:
            print("\n".join(self.term_out))
            self.term_in.append(input())
            self.term_out = [""]
        first_line = self.term_in[0]
        if first_line == "":
            a.set(ord("\n"))
            del self.term_in[0]
            self.term_out.append("") # echo
        else:
            ch = first_line[0]
            a.set(ord(ch))
            first_line = first_line[1:]
            self.term_in[0] = first_line
            self.term_out[-1] += ch # echo

    def instr_noop(self):
        pass

import machine
import file_io
import re
import subprocess
from dataclasses import dataclass, field

@dataclass
class Room:
    name : str = None
    description : [str] = field(default_factory=list)
    items : list[str] = field(default_factory=list)
    exits : dict[str, any] = field(default_factory=dict)
    state : any = None
    __hash : int = None

    def __hash__(self):
        if self.__hash is None:
            self.__hash = hash("\n".join(self.description))
        return self.__hash

    def __eq__(self, othr):
        return (self.description == othr.description)


class MapExplorer:

    def __init__(self, init_state):
        self.machine = machine.Machine()
        self.machine.load(file_io.load_from_file())
        self.search_stack = []
        self.machine.set_term_break("What do you do?")
        self.machine.load_state(file_io.load_state(init_state))
        self.current_room = Room()
        self.prev_room = None
        self.current_exit = None
        self.rooms = set()
        self.found_items = {}

        self.item_to_find = None
        self.description_to_find = None

        self.re_exits = re.compile(r"(There is 1 exit|There are \d+ exits)")

    def explore(self, max_steps, item_to_find = None, description_to_find = None, *actions):
        self.item_to_find = item_to_find
        self.description_to_find = description_to_find
        self.actions = actions
        self.machine.term_in = ["look"]
        for i in range(0, max_steps):
            if not self.search_step():
                break

    def search_step(self):
        self.search_room()
        cont = True
        if not self.already_visited():
            cont = self.process_findings()
        if not cont:
            return False 
        return self.next_room()

    def go(self, *dirs):
        if self.current_room is None:
            self.machine.term_in = ["look"]
            self.go_step()
        for d in dirs:
            self.go_next(d)
            self.go_step()

    def go_step(self):
        self.search_room()
        self.process_findings()

    def search_room(self):
        NONE = 0
        ITEMS = 1
        EXITS = 2

        self.machine.run()
        self.current_room = Room()
        self.current_room.state = self.machine.get_state()

        state = NONE
        copy_line = False
        for ix, line in enumerate(self.machine.term_out):
            if line == "":
                state = NONE
            elif (state == ITEMS) and (line[0] == "-"):
                self.current_room.items.append(line[2:])
            elif (state == EXITS) and (line[0] == "-"):
                self.current_room.exits[line[2:]] = None
            elif line.startswith("== "):
                self.current_room.name = line[3:-3]
                copy_line = True
            elif line == "Things of interest here:":
                state = ITEMS
            elif self.re_exits.match(line):
                state = EXITS
            elif line == "What do you do?":
                copy_line = False

            if copy_line:
                self.current_room.description.append(line)

        if self.prev_room and self.prev_room == self.current_room:
            self.current_room.description.append("Instance 2")

        if self.prev_room:
            self.prev_room.exits[self.current_exit] = self.current_room  
        
    def process_findings(self):
        self.rooms.add(self.current_room)
        if self.current_room.name == "Fumbling around in the darkness":
            return True

        for item in self.current_room.items:
            self.inspect_item(item)

        if self.item_to_find in self.found_items:
            return False

        if self.description_to_find is not None:
            for line in self.current_room.description:
                if self.description_to_find in line:
                    return False

        for ex in self.current_room.exits:
            self.search_stack.append((self.current_room, ex))

        return True

    def inspect_item(self, item):
        self.machine.term_out = [""]
        self.machine.term_in = [f"look {item}"]
        self.machine.run()
        self.found_items[item] = self.machine.term_out[3:-3]

    def take_item(self, item):
        self.machine.term_out = [""]
        self.machine.term_in = [f"take {item}"]
        self.machine.run()
        
    def use_item(self, item):
        self.machine.term_out = [""]
        self.machine.term_in = [f"use {item}"]
        self.machine.run()
        self.found_items[item] = self.found_items.get(item,[]) + self.machine.term_out[3:-3]

    def show_inventory(self):
        self.machine.term_out = [""]
        self.machine.term_in = ["inv"]
        self.machine.run()
        self.found_items["inv"] = self.found_items.get("inv",[]) + self.machine.term_out[:]


    def next_room(self):
        if len(self.search_stack) == 0:
            return False
        self.prev_room, self.current_exit = self.search_stack.pop()
        self.machine.load_state(self.prev_room.state)
        self.machine.term_in = [f"go {self.current_exit}"]
        self.machine.term_out = [""]
        return True

    def go_next(self, d):
        self.prev_room = self.current_room
        self.current_exit = d
        self.machine.term_in = [f"go {d}"]
        self.machine.term_out = [""]

    def already_visited(self):
        return (self.current_room in self.rooms)

    def write_map(self, name):
        with open(f"resources/steps/{name}.dot", "w") as f:
            node_names = {}
            f.write("digraph {\n")
            for room_num, room in enumerate(self.rooms):
                node_name = f"r{room_num}"
                node_names[room] = node_name
                tooltip = "\\n".join(room.description)
                tooltip = tooltip.replace('"',"'")
                f.write(f'\t{node_name}[label="{room.name}", tooltip="{tooltip}"];\n')
            for from_room in self.rooms:
                for ex, to_room in from_room.exits.items():
                    if to_room is None or to_room.name is None:
                        continue
                    from_node = node_names[from_room]
                    to_node = node_names[to_room]
                    f.write(f'\t{from_node} -> {to_node}[label="{ex}"];\n')
            f.write("}\n")
        subprocess.run(["dot", "-Tsvg", f"-oresources/steps/{name}.svg", f"resources/steps/{name}.dot"] )
    
    def write_item_list(self, name):
        with open(f"resources/steps/{name}", "w") as f:
            for item, description in self.found_items.items():
                f.write(f"{item}\n")
                description = "\n".join(description)
                f.write(f"{description}\n\n")

    def save_state(self, name):
        state = self.machine.get_state()
        file_io.save_state(state, name)

    def continue_interactive(self):
        self.machine.set_term_break(None)
        self.machine.run()
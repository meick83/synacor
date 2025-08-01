import machine
import file_io
import re
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
            self.__hash = hash((self.name,)+tuple(self.description))
        return self.__hash


class MapExplorer:

    def __init__(self):
        self.machine = machine.Machine()
        self.machine.load(file_io.load_from_file())
        self.search_stack = []
        self.machine.set_term_break("What do you do?")
        self.machine.load_state(file_io.load_state("after_selftest"))
        self.current_room = Room()
        self.rooms = set()

        self.reName = re.compile(r"== (.*) ==")
        self.reEmpty = re.compile(r"^$")

    def search_step(self):
        self.search_room()
        if self.already_visited():
            return
        self.process_findings()
        self.next_room()

    def search_room(self):
        self.machine.run()
        self.current_room.state = self.machine.get_state()

        it = iter(self.machine.term_out)
        for line in it:
            if line.startswith("== "):
                self.current_room.name = line[3:-3]
                break

        for line in it:
            if line == "":
                break
            self.current_room.description.append(line)

        line = next(it)

        if line == "Things of interest here:":
            for line in it:
                if line == "":
                    line = next(it)
                    break
                self.current_room.items.append(line[2:])

        
        if line.startswith("There are"):
            for line in it:
                if line == "":
                    break
                self.current_room.exits[line[2:]] = None
        
    def process_findings(self):
        self.rooms.add(self.current_room)
        for ex in self.current_room.exits:
            self.search_stack.append((self.current_room, ex))

    def next_room(self):
        start_room, ex = self.search_stack.pop()
        self.machine.load_state(start_room.state)
        self.current_room = Room()
        start_room.exits[ex] = self.current_room
        self.machine.term_in = [f"go {ex}"]
        self.machine.term_out = [""]

    def already_visited(self):
        return (self.current_room in self.rooms)

    def write_dot(self, name):
        with open(name, "w") as f:
            node_names = {}
            f.write("digraph {\n")
            for room_num, room in enumerate(self.rooms):
                node_name = f"r{room_num}"
                node_names[room] = node_name
                description = room.description[:]
                if len(room.items) > 0:
                    description.append("items: "+", ".join(room.items))
                tooltip = "\\n".join(description)
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
    

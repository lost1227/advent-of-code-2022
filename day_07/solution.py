from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

class DirectoryNode:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.children = {}

        self.__size = -1

    def __str__(self):
        out = f"- {self.name} (dir, totsize={self.size})\n"
        children = list(self.children.values())
        for i, child in enumerate(children):
            childstr = "\n".join(["  " + part for part in str(child).strip().split("\n")])
            out += childstr
            if i != len(children)-1:
                out += "\n"
        return out

    @property
    def size(self):
        if self.__size >= 0:
            return self.__size

        children = list(self.children.values())
        self.__size = 0
        for child in children:
            self.__size += child.size
        return self.__size

    @property
    def subdirs(self):
        yield self
        children = list(self.children.values())
        for child in children:
            if isinstance(child, DirectoryNode):
                for subdir in child.subdirs:
                    yield subdir

    @property
    def files(self):
        children = list(self.children.values())
        for child in children:
            if isinstance(child, DirectoryNode):
                for subfile in child.files:
                    yield subfile
            elif isinstance(child, FileNode):
                yield child

class FileNode:
    def __init__(self, name, parent, size):
        self.name = name
        self.parent = parent
        self.size = size

    def __str__(self):
        return f"- {self.name} (file, size={self.size})"

sample_input = """
$ cd /
$ ls
dir a
14848514 b.txt
8504156 c.dat
dir d
$ cd a
$ ls
dir e
29116 f
2557 g
62596 h.lst
$ cd e
$ ls
584 i
$ cd ..
$ cd ..
$ cd d
$ ls
4060174 j
8033020 d.log
5626152 d.ext
7214296 k
"""[1:]

if USE_SAMPLE_INPUT:
    input = sample_input.split("\n")
else:
    with in_path.open("r") as inf:
        input = [line[:-1] for line in inf.readlines()]

root = DirectoryNode("/", None)
curr = root

for line in input:
    if line == "":
        continue
    elif line[0] == "$":
        if line[2:4] == "cd":
            to = line[5:]
            if to == "..":
                curr = curr.parent
            elif to == "/":
                curr = root
            else:
                curr = curr.children[to]
        elif line[2:4] == "ls":
            pass
        else:
            raise ValueError(f"Unrecognized cmd: \"{line[2:4]}\"")
    elif line[0:3] == "dir":
        dirname = line[4:]
        if dirname not in curr.children:
            curr.children[dirname] = DirectoryNode(dirname, curr)
    else:
        size, name = line.split()
        size = int(size)
        if name in curr.children:
            assert curr.children[name].size == size
        else:
            curr.children[name] = FileNode(name, curr, size)

totalsize = 0
for d in root.subdirs:
    if d.size < 100000:
        totalsize += d.size

print("Part 1:", totalsize)

free_space = 70000000 - root.size
space_needed = 30000000 - free_space

min_d = root

for d in root.subdirs:
    if d.size < space_needed:
        continue
    if d.size < min_d.size:
        min_d = d

print("Part 2:", min_d.size)

from pathlib import Path

USE_SAMPLE_INPUT = False
in_path = Path.cwd() / 'input.txt'

sample_input = """
addx 15
addx -11
addx 6
addx -3
addx 5
addx -1
addx -8
addx 13
addx 4
noop
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx -35
addx 1
addx 24
addx -19
addx 1
addx 16
addx -11
noop
noop
addx 21
addx -15
noop
noop
addx -3
addx 9
addx 1
addx -3
addx 8
addx 1
addx 5
noop
noop
noop
noop
noop
addx -36
noop
addx 1
addx 7
noop
noop
noop
addx 2
addx 6
noop
noop
noop
noop
noop
addx 1
noop
noop
addx 7
addx 1
noop
addx -13
addx 13
addx 7
noop
addx 1
addx -33
noop
noop
noop
addx 2
noop
noop
noop
addx 8
noop
addx -1
addx 2
addx 1
noop
addx 17
addx -9
addx 1
addx 1
addx -3
addx 11
noop
noop
addx 1
noop
addx 1
noop
noop
addx -13
addx -19
addx 1
addx 3
addx 26
addx -30
addx 12
addx -1
addx 3
addx 1
noop
noop
noop
addx -9
addx 18
addx 1
addx 2
noop
noop
addx 9
noop
noop
noop
addx -1
addx 2
addx -37
addx 1
addx 3
noop
addx 15
addx -21
addx 22
addx -6
addx 1
noop
addx 2
addx 1
noop
addx -10
noop
noop
addx 20
addx 1
addx 2
addx 2
addx -6
addx -11
noop
noop
noop
""".strip()

class CPU:
    def __init__(self, instructions, cycle_callback):
        self.X = 1
        self.next_X = 1
        self.instructions = iter(instructions)
        self.curr_inst = None
        self.clocks_remaining_in_curr_inst = 0
        self.cycle_callback = cycle_callback

        self.clock = 1

    def _start_of_cycle(self):
        if self.clocks_remaining_in_curr_inst == 0:
            self.curr_inst = next(self.instructions)
            if self.curr_inst == 'noop':
                self.clocks_remaining_in_curr_inst = 1
                self.next_X = self.X
            else:
                inst, imm = self.curr_inst.split()
                assert inst == 'addx'
                self.clocks_remaining_in_curr_inst = 2
                self.next_X = self.X + int(imm)

    def _during_cycle(self):
        self.cycle_callback(self)

    def _end_of_cycle(self):
        self.clocks_remaining_in_curr_inst -= 1
        if self.clocks_remaining_in_curr_inst == 0:
            self.X = self.next_X

    def run(self):
        try:
            while True:
                self._start_of_cycle()
                self._during_cycle()
                self._end_of_cycle()
                self.clock += 1
        except StopIteration:
            pass



if USE_SAMPLE_INPUT:
    input = sample_input.split('\n')
else:
    with in_path.open("r") as inf:
        input = [line.strip() for line in inf.readlines()]

important_clocks = [20, 60, 100, 140, 180, 220]
sum = 0

def sum_cb(cpu):
    global sum
    if cpu.clock in important_clocks:
        print(f"{cpu.clock} * {cpu.X} = {cpu.clock * cpu.X}")
        sum += cpu.clock * cpu.X

cpu = CPU(input, sum_cb)
cpu.run()
print("Part 1:", sum)

# PART 2
crt = [([' '] * 40) for i in range(6)]
def write_crt(cpu):
    global crt
    crt_pos = (cpu.clock-1) % 40
    crt_row = ((cpu.clock-1) // 40) % 6

    if abs(cpu.X - crt_pos) <= 1:
        crt[crt_row][crt_pos] = '#'
    else:
        crt[crt_row][crt_pos] = '.'


cpu = CPU(input, write_crt)
cpu.run()

for row in crt:
    print(''.join(row))

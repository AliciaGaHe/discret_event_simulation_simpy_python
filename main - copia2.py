import simpy
import random
import logging

logging.basicConfig(level=logging.DEBUG)

random.seed(42)

# Simulation parameters

# Arrival distribution for the parts
partA_arrival_distribution = random.uniform(1, 3)
partB_arrival_distribution = random.uniform(1, 3)

# Capacity for the buffers
buffer_partA_ok_capacity = 1000
buffer_partB_review_capacity = 1000
buffer_partB_ok_capacity = 1000
buffer_partB_ko_capacity = 6
buffer_final_products_capacity = 1000

# Cycle time for the machines in minutes
machine_check_quality_partB_cycle_time = 2
machine_repair_partB_cycle_time = 4
machine_create_final_products_cycle_time = 2

# Simulation time in minutes
simulation_time = 30


class Part(object):
    """This class represents the entities or parts."""

    def __init__(self, env, name):
        self.env = env
        self.name = name


class Store(object):
    """This class represents the place where the parts will be stored."""

    def __init__(self, env, name, capacity):
        self.env = env
        self.name = name
        self.store = simpy.Store(env, capacity=capacity)
        self.total_parts_in = 0
        self.total_parts_out = 0

    def put(self, value):
        return self.store.put(value)

    def get(self):
        return self.store.get()


class MachineCheckQuality(object):
    """
    This class represents the machine where somebody will review the quality of the parts.
    The parts can randomly have defects or not.
    Parts with defects will be stored in a special buffer to be repair by another machine.
    """
    def __init__(self, env, name, input_buffer, cycle_time, failure_rate, output_buffer_ok, output_buffer_ko):
        self.env = env
        self.name = name
        self.input_buffer = input_buffer
        self.cycle_time = cycle_time
        self.failure_rate = failure_rate
        self.output_buffer_ok = output_buffer_ok
        self.output_buffer_ko = output_buffer_ko
        self.total_waiting_time = 0
        self.total_working_time = 0
        self.total_blocking_time = 0
        self.total_parts_in = 0
        self.total_parts_out = 0

        # Start the main process for this machine
        self.process = env.process(self.check_quality())

    def check_quality(self):
        while True:
            # Get a part from the input buffer
            start = self.env.now
            part = yield self.input_buffer.get()
            logging.debug(f'{self.env.now:.2f} Machine {self.name} gets a part from {self.input_buffer.name}')
            # Update the number of parts out the input buffer
            self.input_buffer.total_parts_out += 1
            end = self.env.now
            self.total_waiting_time += end - start

            # Update the total number of parts in the machine
            self.total_parts_in += 1

            # Working time
            yield env.timeout(self.cycle_time)
            self.total_working_time += self.cycle_time

            # Blocking time
            start = self.env.now
            if random.uniform(0, 1) <= self.failure_rate:
                logging.debug(f'{self.env.now:.2f} Machine {self.name} detects a defect')

                yield self.output_buffer_ko.put(part)
                logging.debug(f'{self.env.now:.2f} Machine {self.name} put the part in {self.output_buffer_ko.name}, items={len(self.output_buffer_ko.store.items)} amd capacity={self.output_buffer_ko.store.capacity}')

                # Update the number of parts in the output buffer
                self.output_buffer_ko.total_parts_in += 1

                end = self.env.now
                self.total_blocking_time += end - start

            else:
                logging.debug(f'{self.env.now:.2f} Machine {self.name} does not detect a defect')

                yield self.output_buffer_ok.put(part)
                logging.debug(f'{self.env.now:.2f} Machine {self.name} puts the part in {self.output_buffer_ok.name}, items={len(self.output_buffer_ok.store.items)} and capacity={self.output_buffer_ok.store.capacity}')

                # Update the number of parts in the output buffer
                self.output_buffer_ok.total_parts_in += 1

                end = self.env.now
                self.total_blocking_time += end - start


            # Update the total numer of parts out the machine
            self.total_parts_out += 1


class MachineRepairPart(object):
    """This class represents the machine where somebody will repair the parts that has a defect."""
    def __init__(self, env, name, input_buffer, cycle_time, output_buffer):
        self.env = env
        self.name = name
        self.input_buffer = input_buffer
        self.cycle_time = cycle_time
        self.output_buffer = output_buffer
        self.total_waiting_time = 0
        self.total_working_time = 0
        self.total_blocking_time = 0
        self.total_parts_in = 0
        self.total_parts_out = 0

        # Start the main process for this machine
        self.process = env.process(self.repair_part())

    def repair_part(self):
        while True:
            # Get a part from the input buffer
            start = self.env.now
            part = yield self.input_buffer.get()
            logging.debug(f'{self.env.now:.2f} Machine {self.name} gets a part from {self.input_buffer.name}')
            end = self.env.now
            self.total_waiting_time += end - start

            # Update the number of parts out the input buffer
            self.input_buffer.total_parts_out += 1

            # Update the number of parts in the machine
            self.total_parts_in += 1

            # Working time
            start = self.env.now
            yield env.timeout(self.cycle_time)
            end = self.env.now
            self.total_working_time += end - start

            # Blocking time
            start = self.env.now
            yield self.output_buffer.put(part)
            logging.debug(f'{self.env.now:.2f} Machine {self.name} puts the part in {self.output_buffer.name}, items={len(self.output_buffer.store.items)} and capacity={self.output_buffer.store.capacity}')
            end = self.env.now
            self.total_blocking_time += end - start

            # Update the number of parts out the machine
            self.total_parts_out += 1

            # Update the number of parts in the output buffer
            self.output_buffer.total_parts_in += 1

class MachineCreateFinalProducts(object):
    """This class represents the machine where somebody will join two different raw parts
    to create the final products."""
    def __init__(self, env, name, input_buffer1, input_buffer2, cycle_time, output_buffer):
        self.env = env
        self.name = name
        self.input_buffer1 = input_buffer1
        self.input_buffer2 = input_buffer2
        self.cycle_time = cycle_time
        self.output_buffer = output_buffer
        self.total_waiting_time = 0
        self.total_working_time = 0
        self.total_blocking_time = 0
        self.total_parts_in = 0
        self.total_parts_out = 0

        # Start the main process for this machine
        self.process = env.process(self.create_final_products())

    def create_final_products(self):
        while True:
            # Get parts from the input buffers
            start = self.env.now

            part1 = yield self.input_buffer1.get()
            logging.debug(f'{self.env.now:.2f} Machine {self.name} gets a part from {self.input_buffer1.name}')
            # Update the number of parts in the machine
            self.total_parts_in += 1
            # Update the number of parts out the input buffer1
            self.input_buffer1.total_parts_out += 1

            part2 = yield self.input_buffer2.get()
            logging.debug(f'{self.env.now:.2f} Machine {self.name} gets a part from {self.input_buffer2.name}')
            # Update the number of parts in the machine
            self.total_parts_in += 1
            # Update the number of parts out the input buffer2
            self.input_buffer2.total_parts_out += 1

            end = self.env.now
            self.total_waiting_time += end - start

            # Working time
            start = self.env.now
            yield env.timeout(self.cycle_time)
            end = self.env.now
            self.total_working_time += end - start

            # Blocking time
            start = self.env.now
            yield self.output_buffer.put(part1)
            yield self.output_buffer.put(part2)
            logging.debug(f'{self.env.now:.2f} Machine {self.name} puts final product in {self.output_buffer.name}, items={len(self.output_buffer.store.items)/2} and capacity={self.output_buffer.store.capacity}')
            end = self.env.now
            self.total_blocking_time += end - start

            # Update the number of parts out the machine
            self.total_parts_out += 1

            # Update the number of parts in the output buffer
            self.output_buffer.total_parts_in += 1


def generate_arrivals(env, part, input_buffer, arrival_time):
    """This function generate the part arrival and store them in specific buffers."""

    while True:
        yield env.timeout(arrival_time)
        logging.debug(f'{env.now:.2f} {part.name} has arrived')

        yield input_buffer.put(part)
        logging.debug(f'{env.now:.2f} {part.name} in {input_buffer.name}, items={len(input_buffer.store.items)} and capacity={input_buffer.store.capacity}')

        # Update the number of parts that comes in the input buffer
        input_buffer.total_parts_in += 1


# Create environment
env = simpy.Environment()

# Create the parts
partA = Part(env, name='part_A')
partB = Part(env, name='part_B')

# Create the buffers
buffer_partA_ok = Store(env, name='buffer_part_A_ok', capacity=buffer_partA_ok_capacity)
buffer_partB_review = Store(env, name='buffer_part_B_review', capacity=buffer_partB_review_capacity)
buffer_partB_ok = Store(env, name='buffer_part_B_ok', capacity=buffer_partB_ok_capacity)
buffer_partB_ko = Store(env, name='buffer_part_B_ko', capacity=buffer_partB_ko_capacity)
buffer_final_products = Store(env, name='buffer_final_products', capacity=buffer_final_products_capacity)

# Create the machines
machine_check_quality_partB = MachineCheckQuality(
    env,
    name='machine_check_quality_part_B',
    input_buffer=buffer_partB_review,
    cycle_time=machine_check_quality_partB_cycle_time,
    failure_rate=0.3,
    output_buffer_ok=buffer_partB_ok,
    output_buffer_ko=buffer_partB_ko
)
machine_repair_partB = MachineRepairPart(
    env,
    name='machine_repair_part_B',
    input_buffer=buffer_partB_ko,
    cycle_time=machine_repair_partB_cycle_time,
    output_buffer=buffer_partB_ok
)
machine_create_final_products = MachineCreateFinalProducts(
    env,
    name='machine_create_final_products',
    input_buffer1=buffer_partA_ok,
    input_buffer2=buffer_partB_ok,
    cycle_time=machine_create_final_products_cycle_time,
    output_buffer=buffer_final_products
)

# Create the parts arrivals. The machines __init__ starts the machine process so no env.process() is needed here
env.process(generate_arrivals(env, part=partA, input_buffer=buffer_partA_ok, arrival_time=partA_arrival_distribution))
env.process(generate_arrivals(env, part=partB, input_buffer=buffer_partB_review, arrival_time=partB_arrival_distribution))

# Run the simulation
env.run(until=simulation_time)

print("\n")
print("buffer_partA_ok - main statistics")
print(f'total_parts_in = {buffer_partA_ok.total_parts_in}')
print(f'total_parts_out = {buffer_partA_ok.total_parts_out}')
print(f'parts_now_in = {buffer_partA_ok.total_parts_in - buffer_partA_ok.total_parts_out}')

print("\n")
print("buffer_partB_review - main statistics")
print(f'total_parts_in = {buffer_partB_review.total_parts_in}')
print(f'total_parts_out = {buffer_partB_review.total_parts_out}')
print(f'parts_now_in = {buffer_partB_review.total_parts_in - buffer_partB_review.total_parts_out}')

print("\n")
print("buffer_partB_ok - main statistics")
print(f'total_parts_in = {buffer_partB_ok.total_parts_in}')
print(f'total_parts_out = {buffer_partB_ok.total_parts_out}')
print(f'parts_now_in = {buffer_partB_ok.total_parts_in - buffer_partB_ok.total_parts_out}')

print("\n")
print("buffer_partB_ko - main statistics")
print(f'total_parts_in = {buffer_partB_ko.total_parts_in}')
print(f'total_parts_out = {buffer_partB_ko.total_parts_out}')
print(f'parts_now_in = {buffer_partB_ko.total_parts_in - buffer_partB_ko.total_parts_out}')

print("\n")
print("buffer_final_products - main statistics")
print(f'parts_total_in = {buffer_final_products.total_parts_in}')
print(f'parts_total_out = {buffer_final_products.total_parts_out}')
print(f'parts_now_in = {buffer_final_products.total_parts_in - buffer_final_products.total_parts_out}')

print("\n")
print("machine_check_quality_partB - main statistics")
print(f'%_waiting_time = {(machine_check_quality_partB.total_waiting_time / simulation_time) * 100:.2f} %')
print(f'%_working_time = {(machine_check_quality_partB.total_working_time / simulation_time) * 100:.2f} %')
print(f'%_blocking_time = {(machine_check_quality_partB.total_blocking_time / simulation_time) * 100:.2f} %')
print(f'total_parts_in = {machine_check_quality_partB.total_parts_in}')
print(f'total_parts_out = {machine_check_quality_partB.total_parts_out}')

print("\n")
print("machine_repair_partB - main statistics")
print(f'%_waiting_time = {(machine_repair_partB.total_waiting_time / simulation_time) * 100:.2f} %')
print(f'%_working_time = {(machine_repair_partB.total_working_time / simulation_time) * 100:.2f} %')
print(f'%_blocking_time = {(machine_repair_partB.total_blocking_time / simulation_time) * 100:.2f} %')
print(f'total_parts_in = {machine_repair_partB.total_parts_in}')
print(f'total_parts_out = {machine_repair_partB.total_parts_out}')

print("\n")
print("machine_create_final_products - main statistics")
print(f'%_waiting_time = {(machine_create_final_products.total_waiting_time / simulation_time) * 100:.2f} %')
print(f'%_working_time = {(machine_create_final_products.total_working_time / simulation_time) * 100:.2f} %')
print(f'%_blocking_time = {(machine_create_final_products.total_blocking_time / simulation_time) * 100:.2f} %')
print(f'total_parts_in = {machine_create_final_products.total_parts_in}')
print(f'total_parts_out = {machine_create_final_products.total_parts_out}')

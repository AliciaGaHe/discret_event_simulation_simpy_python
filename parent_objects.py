import simpy
import random
import logging

logging.basicConfig(level=logging.DEBUG)


class Part(object):
    """This class represents the entities or parts."""

    def __init__(self, env, name, arrival_time_lower_boundary, arrival_time_upper_boundary, batch_size, input_buffer):
        self.env = env
        self.name = name
        self.arrival_time_lower_boundary = arrival_time_lower_boundary
        self.arrival_time_upper_boundary = arrival_time_upper_boundary
        self.batch_size = batch_size
        self.input_buffer = input_buffer

    def generate_arrivals(self):
        """This method generates the part arrivals and puts them in the correct input buffer"""

        while True:
            # Generate the inter arrival time using a uniform distribution and wait until the next arrival
            yield self.env.timeout(random.uniform(self.arrival_time_lower_boundary, self.arrival_time_upper_boundary))
            logging.debug(f'{self.env.now:.2f} {self.name} has arrived with batch_size={self.batch_size}')

            # More than one part can arrive at the same time
            for num_parts in range(self.batch_size):
                # Put the part in the correct buffer
                yield self.input_buffer.put(self.name)
                logging.debug(
                    f'{self.env.now:.2f} {self.name} in {self.input_buffer.name}, items={len(self.input_buffer.store.items)} and capacity={self.input_buffer.store.capacity}')

                # Update the number of parts that comes in the input buffer
                self.input_buffer.total_parts_in += 1


class Store(object):
    """This class represents the place where the parts will be stored"""

    def __init__(self, env, name, capacity):
        self.env = env
        self.name = name
        self.store = simpy.Store(env, capacity=capacity)
        self.total_parts_in = 0
        self.total_parts_out = 0

    def get(self):
        """This method is used to get a part from a buffer"""
        return self.store.get()

    def put(self, part):
        """This method is used to put a part in a buffer"""
        return self.store.put(part)


class MachineCheckQuality(object):
    """
    This class represents the machine where somebody will review the quality of the parts.
    The parts can randomly have a defect or not.
    Parts with defects will be stored in a special buffer to be repaired by another machine.
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

    def check_quality(self):
        """This method takes a part from an input buffer, reviews its quality and put it in an output buffer if
        it has a defect or in another if it does not have any defect"""

        while True:
            # Get a part from the input buffer
            start = self.env.now
            part = yield self.input_buffer.get()
            logging.debug(f'{self.env.now:.2f} Machine {self.name} gets a part from {self.input_buffer.name}')
            # Update the number of parts out the input buffer
            self.input_buffer.total_parts_out += 1
            end = self.env.now
            # Update the time that the machine have to wait for a part
            self.total_waiting_time += end - start

            # Update the total number of parts in the machine
            self.total_parts_in += 1

            # Working time
            start = self.env.now
            yield self.env.timeout(self.cycle_time)
            end = self.env.now
            self.total_working_time += end - start

            # Blocking time
            start = self.env.now
            if random.uniform(0, 1) <= self.failure_rate:
                logging.debug(f'{self.env.now:.2f} Machine {self.name} detects a defect')

                yield self.output_buffer_ko.put(part)
                logging.debug(f'{self.env.now:.2f} Machine {self.name} put the part in {self.output_buffer_ko.name}, items={len(self.output_buffer_ko.store.items)} amd capacity={self.output_buffer_ko.store.capacity}')

                # Update the number of parts with a defect in the output buffer
                self.output_buffer_ko.total_parts_in += 1

                end = self.env.now
                self.total_blocking_time += end - start

            else:
                logging.debug(f'{self.env.now:.2f} Machine {self.name} does not detect a defect')

                yield self.output_buffer_ok.put(part)
                logging.debug(f'{self.env.now:.2f} Machine {self.name} puts the part in {self.output_buffer_ok.name}, items={len(self.output_buffer_ok.store.items)} and capacity={self.output_buffer_ok.store.capacity}')

                # Update the number of parts without a defect in the output buffer
                self.output_buffer_ok.total_parts_in += 1

                end = self.env.now
                self.total_blocking_time += end - start

            # Update the total numer of parts out the machine
            self.total_parts_out += 1


class MachineRepairPart(object):
    """This class represents the machine where somebody will repair the parts that have a defect."""
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

    def repair_part(self):
        """This method takes a part from an input buffer, repairs it and puts it an output buffer"""
        while True:
            # Get a part from the input buffer
            start = self.env.now
            part = yield self.input_buffer.get()
            logging.debug(f'{self.env.now:.2f} Machine {self.name} gets a part from {self.input_buffer.name}')
            end = self.env.now
            # Update the time that the machine have to wait for a part
            self.total_waiting_time += end - start

            # Update the number of parts out the input buffer
            self.input_buffer.total_parts_out += 1

            # Update the number of parts in the machine
            self.total_parts_in += 1

            # Working time
            start = self.env.now
            yield self.env.timeout(self.cycle_time)
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
    to create a final product"""
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

    def create_final_products(self):
        """This method takes a part from an input buffer and another part from another input buffer and joins then to
        create a final product that put it in an output buffer"""
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
            # Update the time that the machine have to wait for a part
            self.total_waiting_time += end - start

            # Working time
            start = self.env.now
            yield self.env.timeout(self.cycle_time)
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

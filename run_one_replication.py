# Import from libraries
import simpy
import random
import pandas as pd
import logging

# Import from files
from parent_objects import Part, Store, MachineCheckQuality, MachineRepairPart, MachineCreateFinalProducts

logging.basicConfig(level=logging.DEBUG)


def run_one_replication(
        replication_number,
        partA_arrival_distribution_lower_boundary,
        partA_arrival_distribution_upper_boundary,
        partB_arrival_distribution_lower_boundary,
        partB_arrival_distribution_upper_boundary,
        partA_batch_size,
        partB_batch_size,
        buffer_partA_ok_capacity,
        buffer_partB_review_capacity,
        buffer_partB_ok_capacity,
        buffer_partB_ko_capacity,
        buffer_final_products_capacity,
        machine_check_quality_partB_cycle_time,
        machine_repair_partB_cycle_time,
        machine_create_final_products_cycle_time,
        failure_rate_partB,
        simulation_time
):
    """This function includes all we need to create the simulation model and run it one time.
    As result, we get information about the main output for parts, buffers and machines."""

    logging.debug('\n')
    logging.debug(f'Iteration: {replication_number + 1}')
    logging.debug('\n')

    # Fix the seed to get the same output each time that we run the simulation
    seed = 40 + replication_number
    random.seed(seed)

    # Create environment
    env = simpy.Environment()

    # Create the objects

    # Create the buffers (we create the buffers first because they are input for Parts and Machines)
    buffer_partA_ok = Store(env, name='b_A_ok', capacity=buffer_partA_ok_capacity)
    buffer_partB_review = Store(env, name='b_B_?', capacity=buffer_partB_review_capacity)
    buffer_partB_ok = Store(env, name='b_B_ok', capacity=buffer_partB_ok_capacity)
    buffer_partB_ko = Store(env, name='b_B_ko', capacity=buffer_partB_ko_capacity)
    buffer_final_products = Store(env, name='b_finals', capacity=buffer_final_products_capacity)

    # Create the parts
    partA = Part(
        env,
        name='part_A',
        arrival_time_lower_boundary=partA_arrival_distribution_lower_boundary,
        arrival_time_upper_boundary=partA_arrival_distribution_upper_boundary,
        batch_size=partA_batch_size,
        input_buffer=buffer_partA_ok
    )
    partB = Part(
        env,
        name='part_B',
        arrival_time_lower_boundary=partB_arrival_distribution_lower_boundary,
        arrival_time_upper_boundary=partB_arrival_distribution_upper_boundary,
        batch_size=partB_batch_size,
        input_buffer=buffer_partB_review
    )

    # Create the machines
    machine_check_quality_partB = MachineCheckQuality(
        env,
        name='m_check_B',
        input_buffer=buffer_partB_review,
        cycle_time=machine_check_quality_partB_cycle_time,
        failure_rate=failure_rate_partB,
        output_buffer_ok=buffer_partB_ok,
        output_buffer_ko=buffer_partB_ko
    )
    machine_repair_partB = MachineRepairPart(
        env,
        name='m_repair_B',
        input_buffer=buffer_partB_ko,
        cycle_time=machine_repair_partB_cycle_time,
        output_buffer=buffer_partB_ok
    )
    machine_create_final_products = MachineCreateFinalProducts(
        env,
        name='m_create_finals',
        input_buffer1=buffer_partA_ok,
        input_buffer2=buffer_partB_ok,
        cycle_time=machine_create_final_products_cycle_time,
        output_buffer=buffer_final_products
    )

    # Launch the events

    # Create the parts arrivals
    env.process(partA.generate_arrivals())
    env.process(partB.generate_arrivals())

    # Start main process for each machine
    env.process(machine_check_quality_partB.check_quality())
    env.process(machine_repair_partB.repair_part())
    env.process(machine_create_final_products.create_final_products())

    # Run the simulation
    env.run(until=simulation_time)

    # Print the main outputs
    logging.debug("\n")
    logging.debug("Part main statistics")

    dict_parts_statistics = {
        'statistics': [
            '1_total_parts_in',
            '2_total_ok_used',
            '3_total_created',
        ],
        partA.name: [
            buffer_partA_ok.total_parts_in,
            buffer_partA_ok.total_parts_out,
            0,
        ],
        partB.name: [
            buffer_partB_review.total_parts_in,
            buffer_partB_ok.total_parts_out,
            0,
        ],
        'finals': [
            0,
            0,
            buffer_final_products.total_parts_in,
        ],
    }

    df_parts_statistics = pd.DataFrame(dict_parts_statistics)

    logging.debug(df_parts_statistics)

    logging.debug("\n")
    logging.debug("Buffer main statistics")

    dict_buffers_statistics = {
        'statistics': [
            '1_total_in',
            '2_total_out',
            '3_in_now',
        ],
        buffer_partA_ok.name: [
            buffer_partA_ok.total_parts_in,
            buffer_partA_ok.total_parts_out,
            buffer_partA_ok.total_parts_in - buffer_partA_ok.total_parts_out,
        ],
        buffer_partB_review.name: [
            buffer_partB_review.total_parts_in,
            buffer_partB_review.total_parts_out,
            buffer_partB_review.total_parts_in - buffer_partB_review.total_parts_out,
        ],
        buffer_partB_ko.name: [
            buffer_partB_ko.total_parts_in,
            buffer_partB_ko.total_parts_out,
            buffer_partB_ko.total_parts_in - buffer_partB_ko.total_parts_out,
        ],
        buffer_partB_ok.name: [
            buffer_partB_ok.total_parts_in,
            buffer_partB_ok.total_parts_out,
            buffer_partB_ok.total_parts_in - buffer_partB_ok.total_parts_out,
        ],
        buffer_final_products.name: [
            buffer_final_products.total_parts_in,
            buffer_final_products.total_parts_out,
            buffer_final_products.total_parts_in - buffer_final_products.total_parts_out,
        ]
    }

    df_buffers_statistics = pd.DataFrame(dict_buffers_statistics)

    logging.debug(df_buffers_statistics)

    logging.debug("\n")
    logging.debug("Machine main statistics")

    dict_machines_statistics = {
        'statistics': [
            '1_%_waiting_time',
            '2_%_working_time',
            '3_%_blocking_time',
            '4_total_parts_in',
            '5_total_parts_out',
            '6_parts_in_now',
        ],
        machine_check_quality_partB.name: [
            round((machine_check_quality_partB.total_waiting_time / simulation_time) * 100, 2),
            round((machine_check_quality_partB.total_working_time / simulation_time) * 100, 2),
            round((machine_check_quality_partB.total_blocking_time / simulation_time) * 100, 2),
            machine_check_quality_partB.total_parts_in,
            machine_check_quality_partB.total_parts_out,
            machine_check_quality_partB.total_parts_in - machine_check_quality_partB.total_parts_out,
        ],
        machine_repair_partB.name: [
            round((machine_repair_partB.total_waiting_time / simulation_time) * 100, 2),
            round((machine_repair_partB.total_working_time / simulation_time) * 100, 2),
            round((machine_repair_partB.total_blocking_time / simulation_time) * 100, 2),
            machine_repair_partB.total_parts_in,
            machine_repair_partB.total_parts_out,
            machine_repair_partB.total_parts_in - machine_repair_partB.total_parts_out,
        ],
        machine_create_final_products.name: [
            round((machine_create_final_products.total_waiting_time / simulation_time) * 100, 2),
            round((machine_create_final_products.total_working_time / simulation_time) * 100, 2),
            round((machine_create_final_products.total_blocking_time / simulation_time) * 100, 2),
            machine_create_final_products.total_parts_in,
            machine_create_final_products.total_parts_out,
            machine_create_final_products.total_parts_in - machine_create_final_products.total_parts_out * 2,
        ]
    }
    df_machines_statistics = pd.DataFrame(dict_machines_statistics)

    logging.debug(df_machines_statistics)

    return df_parts_statistics, df_buffers_statistics, df_machines_statistics

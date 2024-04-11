# Import from files
from run_several_replications import run_several_replications

# Simulation parameters

# Arrival distribution parameters for each part
partA_arrival_distribution_lower_boundary = 1
partA_arrival_distribution_upper_boundary = 4
partB_arrival_distribution_lower_boundary = 1.5
partB_arrival_distribution_upper_boundary = 2.5

# Batch size for each part
partA_batch_size = 2
partB_batch_size = 1

# Capacity for the buffers
buffer_partA_ok_capacity = 100
buffer_partB_review_capacity = 100
buffer_partB_ok_capacity = 100
buffer_partB_ko_capacity = 1
buffer_final_products_capacity = 100

# Cycle time (in minutes) for the machines
machine_check_quality_partB_cycle_time = 2
machine_repair_partB_cycle_time = 5
machine_create_final_products_cycle_time = 2

# Failure rate for partB
failure_rate_partB = 0.4

# Simulation time (in minutes)
simulation_time = 60

# Number of replication to run
num_replications = 20

# Alpha for the confidence interval
alpha = 0.05

run_several_replications(
        alpha,
        num_replications,
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
)

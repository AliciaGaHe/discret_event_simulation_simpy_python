# Import from libraries
import pandas as pd

# Import from files
from run_one_replication import run_one_replication
from tools import confidence_interval


def run_several_replications(
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
):
    """This function includes all we need to run several replications of the simulation model.
    As result, we get information about the main output for parts, buffers and machines
    (mean and confidence interval for the mean for eah output)"""

    df_parts_statistics = pd.DataFrame()
    df_buffers_statistics = pd.DataFrame()
    df_machines_statistics = pd.DataFrame()

    for replication_number in range(num_replications):

        df_parts_statistics_aux, df_buffers_statistics_aux, df_machines_statistics_aux = run_one_replication(
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
        )

        df_parts_statistics = pd.concat([df_parts_statistics, df_parts_statistics_aux])
        df_buffers_statistics = pd.concat([df_buffers_statistics, df_buffers_statistics_aux])
        df_machines_statistics = pd.concat([df_machines_statistics, df_machines_statistics_aux])

    print("\n")
    print("Part main statistics")

    print(
        df_parts_statistics.groupby('statistics').agg(
            lambda x: confidence_interval(values=x, alpha=alpha, num_replications=replication_number)
        ).reset_index()
    )

    print("\n")
    print("Buffer main statistics")

    print(
        df_buffers_statistics.groupby('statistics').agg(
            lambda x: confidence_interval(values=x, alpha=alpha, num_replications=replication_number)
        ).reset_index()
    )

    print("\n")
    print("Machine main statistics")

    print(
        df_machines_statistics.groupby('statistics').agg(
            lambda x: confidence_interval(values=x, alpha=alpha, num_replications=replication_number)
        ).reset_index()
    )

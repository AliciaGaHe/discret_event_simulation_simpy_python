Here we use simpy library in order to create a digital twin of a production system. This digital twin will be used to analyse the performance of the system and to evaluate different changes in its operation.

The code is divided in several files:
	* parent_objects.py. Here we can find the parent objects that we have designed to create the real elements to simulate.
	* run_one_replication.py. 'run_one_replication' funtion includes all we need to create the simulation model and run it one time. As result, we get information about the main outputs for parts, buffers and machines.
	* run_several_replications.py. 'run_several_replications' function includes all we need to run several replications of the simulation model. As result, we get information about the main outputs for parts, buffers and machines (mean and confidence interval for the mean for each output).
	* tools. 'confidence_interval' function returns the confidence interval for the mean of a set of values.
	* test_scenario_x.py. File to run the scenario 'x'.

test_scenario_0.py (scenario 0). Here we have the initial situation:
	* We have two parts ('part_A' and 'part_B') that arrives at the system following uniform distributions.
	* The batch size is equal to 2 for parts A and equal to 1 for parts B.
	* When parts A arrive to the system, they are stored in a buffer ('b_A_ok') until they are used.
	* Parts B are stored in another buffer ('b_B_?') where they wait for a quality control.
	* This control will be made by a machine ('m_check_B') and takes 2 minutes.
	* If this machine does not detect any defect, the part will be stored in the buffer 'b_B_ok'.
	* However, a defect is found in 40% of the controls and the part is put in the buffer 'b_B_ko' until its reparation.
	* We have a machine ('m_repair_B') that gets parts from the buffer 'b_B_ko', repairs it and puts it in the buffer 'b_B_ok'. The reparation takes 5 minutes.
	* Finally, we have a machine ('m_create_finals') that gets one part A from 'b_A_ok' and one part B from 'b_B_ok' and joins them in a final product that is stored in 'b_finals'. This process takes 5 minutes.
	* The capacity of all buffers is 100, except for the buffer 'b_B_ko' whose capacity is equal to 1.

Using this data, we want to know the performance of the system during 60 minutes. As we have some random input data, one replication will not represent the real behaviour of the system. Then we have run 20 replications, each of them with different random numbers.

Here the objective is to produce the maximum number of final products with the resources that we have.

test_scenario_0_output.PNG shows main statistics for parts, buffers and machines (mean and confidence interval with alpha = 0.05 for the mean for each output). In mean:
	* 22.2 final products are produced.
	* 'm_create_finals' is waiting for parts during 24.4% of the simulation time because it has to wait for parts at the begining of the simulation and while parts B are being checked and repared.
	* 'b_B_ko' (with capacity equal to one part) and 'm_repair_B' (with a high utilization, equal to 71.7%) are bottlenecks in some specific moments and this produces that 'm_check_B' is blocked during a 10.2% of the simulation time.

test_scenario_1.py (scenario 1). Using the scenario 0, we have increased the capacity for 'b_B_ko' from 1 to 2 (buffer_partB_ko_capacity = 2). If we compare scenario 0 and 1:
	* '3_%_blocking_time' for 'm_check_B' is reduced, in mean, from 10.2% in secenario 0 (see test_scenario_0_output.PNG) to 7.7% in secenario 1 (see test_scenario_1_output.PNG) and this increases a bit the productivity of this machine (2_%_working_time and 5_total_parts_out). Here the confidence intervals are overlaped between secenarios. Therefore we have not a real improvement.
	* Moreover, we do not find a real improvement in the '3_total_created' for 'finals' because the confidence intervals for the scenarios 0 and 1 are overlaped.

test_scenario_2.py (scenario 2). Using the scenario 1, we have increased the capacity for 'b_B_ko' from 2 to 3 (buffer_partB_ko_capacity = 3). If we compare scenario 1 and 2:
	* '3_%_blocking_time' for 'm_check_B' and '3_total_created' for 'finals' improve in mean. However the confidence intervals for the scenarios 1 (see test_scenario_1_output.PNG) and 2 (see test_scenario_2_output.PNG) are overlaped. Therefore there is not a real improvement in all the studied scenarios.

test_scenario_3.py (scenario 3). Using the scenario 2, we reduce the cycle time for 'm_check_B' machine giving a special trainig to the person who works there (machine_check_quality_partB_cycle_time = 1.5). If we compare scenario 0 and 3:
	* '3_%_blocking_time' for 'm_check_B' is reduced, in mean, from 10.2% in secenario 0 (see test_scenario_0_output.PNG) to 3.4% in scenario 3 (see test_scenario_3_output.PNG). Here the confidence intervals are overlaped between secenarios. Therefore we have not a real improvement.
	* We can also see an increase in the '5_total_parts_out' for 'm_check_B' from 25.1 in scenario 0 to 28.4 in scenario 3. Here the confidence intervals are also overlaped between secenarios. Therefore we have not a real improvement.
	* As we have more parts B in 'b_B_ok', 'm_create_finals' has more utilization (2_%_working_time) and at the end, more 'finals' are produced in mean. However, the confidence intervals are overlaped between secenarios. Therefore we have not a real improvement.
	
With this easy example, we can see how simulation is a good tool to analyse what-if scenarios. Also notice that we should compare the profit of each change with its cost before to take a decision. Here we do not considere costs.

(If you show small changes in the arrivals that is because we are using the same seed to manage all the randon distributions that we have in our simulation model. It would be better to use one different seed for each random distribution.)

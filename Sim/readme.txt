RUNNING THE SCRIPT ON COMMAND LINE:
	Once project folder has been imported and directory is set to project folder:
	Commandline: python3 main.py arg1 arg2 arg3 arg4 
	      arg1: Scheduling Algorithm (1 - FCFS, 2 - SRTF, 3 - HRRN, 4 - RR)
              arg2: Process Arrival Rate
              arg3: Average Service Time
              arg4: Quantum (only for RR scheduler)
	      arg5: Loop scheduler mode: If 'True' argument given, algorithm automatically loops for lambda = 10 to lambda = 30 and outputs to simdata.csv
					If 'False argument given, algorithm executes one time for given arrival rate and appends metrics to simdata.csv

Example script call:
	python3 main.py 1 10 .04 .01 True


 Included in the project folder are sample runs for all 20 lambdas
labelled by scheduling algorithm. These sample data files were used to create the report in Jupyter which I then exported to a pdf a
nd included in the project folder.

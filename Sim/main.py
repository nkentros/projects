import sys
import random
import math

""""
Description: This program simulates four different scheduling algorithms and measures various performance metrics.

Command line parameters:
              Parameter 1: Scheduling Algorithm (1 - FCFS, 2 - SRTF, 3 - HRRN, 4 - RR)
              Parameter 2: Process Arrival Rate
              Parameter 3: Average Service Time
              Parameter 4: Quantum (only for RR scheduler)
              Parameter 5: Run scheduler from lambda = 10 to 30 (True/False
            
        Scheduling algorithms:
        1. First Come First Served : Non pre emptive, places processes in ready queue and services sequentially.
        2. Shortest Time Remaining First : Pre emptive, sorts ready_queue based on lowest remaining service time. 
            New arrivals can take the place of active processes.
        3. Highest Response Ratio Next: Non pre emptive, services processes in order based on highest response ratio.
        4. Round Robin : Pre emptive, uses an interval specified by quantum parameter. Each quantum, the scheduler will 
            preempt the active process and move it back to the end of the ready_queue. Services on FCFS basis.
            
This simulator is event based. Each iteration of the algorithm looks at the next event in event_queue and processes it.
Scheduled arrivals enter the ready queue and the next arrival is generated and placed into the event queue.
Scheduled departures are placed into a list of completed processes.
CPU utilization is tracked and processes are assumed to be using 100% of the CPU when they are being servied.
"""


def main():
    # Initialization
    arrival_rate = 10
    avg_service_time = 0.04
    num_processes = 10000
    quantum = .01
    algorithm = 1
    loop_algorithm = True
    try:
        algorithm = int(sys.argv[1])
    except IndexError:
        print("""Parameter usage:
              Parameter 1: Scheduling Algorithm (1 - FCFS, 2 - SRTF, 3 - HRRN, 4 - RR)
              Parameter 2: Process Arrival Rate
              Parameter 3: Average Service Time (seconds)
              Parameter 4: Quantum (only for RR scheduler)
              Parameter 5: Set Loop Mode True/False (Lambda=10 to 30)
              """)
    try:
        arrival_rate = float(sys.argv[2])
    except IndexError:
        pass
    try:
        avg_service_time = float(sys.argv[3])
    except IndexError:
        pass
    try:
        quantum = float(sys.argv[4])
    except IndexError:
        pass
    try:
        loop_algorithm = bool(sys.argv[5])
    except IndexError:
        pass

    srate = 1 / avg_service_time
    columns = ['arrival_rate', 'service rate', 'avg turnaround', 'total throughput', 'cpu util', 'avg#processes']

    # Normal program run: simulates chosen algorithms and outputs metrics
    # Note: In this state data will be appended to corresponding data file, not overwritten. If running multiple
    # simulations like this, clear simdata.csv before beginning
    if loop_algorithm is False:
        f = open('simdata.csv', 'w')
        for i in range(len(columns)):
            f.write(columns[i])
            if i < len(columns) - 1:
                f.write(',')
        f.write('\n')
        f.close()
        if algorithm == 1:
            fcfs(arrival_rate, srate, num_processes)
        elif algorithm == 2:
            srtf(arrival_rate, srate, num_processes)
        elif algorithm == 3:
            hrrn(arrival_rate, srate, num_processes)
        elif algorithm == 4:
            rr(arrival_rate, srate, num_processes, quantum)

    # Functionality provided to choose to run scheduling algorithm 20 times
    # From arrival rate of 10 per second to 30 per second
    # Metrics are outputted to simdata.csv, overwriting the data already there
    if loop_algorithm is True:

        f = open('simdata.csv', 'w')
        for i in range(len(columns)):
            f.write(columns[i])
            if i < len(columns) - 1:
                f.write(',')
        f.write('\n')
        f.close()

        if algorithm == 1:
            for i in range(10, 31):
                fcfs(i, srate, num_processes)
        elif algorithm == 2:
            for i in range(10, 31):
                srtf(i, srate, num_processes)
        elif algorithm == 3:
            for i in range(10, 31):
                hrrn(i, srate, num_processes)
        elif algorithm == 4:
            for i in range(10, 31):
                rr(i, srate, num_processes, quantum)

        print("Success!")


# Using random value between 0 and 1 from random.random(), generates random number at an average given by rate parameter
def gen_rand_time(rate):
    x = 0
    while x == 0:
        u = random.random()
        x = (-1 / rate) * math.log(u)
    return x


# Used to insert an event in the event_queue at the correct time
def insert_event(event, event_queue):
    if len(event_queue) == 0:
        event_queue.append(event)
    elif event_queue[0].type == 'DEPARTURE' and event.arrival < event_queue[0].departure:
        event_queue.insert(0, event)
    else:
        event_queue.append(event)


# Used for the Round Robin scheduler to handle the additional event type Quantum
def insert_event_rr(event, event_queue):
    if len(event_queue) == 0:
        event_queue.append(event)
        return
    elif event.arrival > event_queue[len(event_queue) - 1].event_time():
        event_queue.append(event)
        return
    for i in range(len(event_queue)):
        if event.arrival < event_queue[i].event_time():
            event_queue.insert(i, event)
            break


# Creates a departure event for a given process and adds it to the event_queue
def schedule_departure(departing, event_queue, clock):
    if len(event_queue) == 0:
        event_queue.append(Event('DEPARTURE', departing.arrival, departing.service,
                                 clock + departing.service, 0, clock - departing.arrival))
        return
    if (departing.service + clock) > event_queue[len(event_queue) - 1].arrival:
        event_queue.append(Event('DEPARTURE', departing.arrival, departing.service,
                                 clock + departing.service, 0, clock - departing.arrival))

    # Otherwise iterate through event_queue to find insertion point
    else:
        for i in range(len(event_queue)):
            if departing.service + clock <= event_queue[i].event_time():
                event_queue.insert(i, Event('DEPARTURE', departing.arrival, departing.service,
                                            clock + departing.service, 0, clock - departing.arrival))
                break


# Inserts event at correct position in ready_queue based on its remaining service time
def insert_ordered_srtf(ready, ready_queue, service_time):
    if len(ready_queue) == 0:
        ready_queue.append(Event('READY', ready.arrival, service_time, ready.departure,
                                 ready.turnaround, ready.waiting))
        return
    for i in range(len(ready_queue)):
        if ready.service < ready_queue[i].service:
            ready_queue.insert(i, Event('READY', ready.arrival, service_time, ready.departure,
                                        ready.turnaround, ready.waiting))
            return
    ready_queue.append(Event('READY', ready.arrival, service_time, ready.departure,
                             ready.turnaround, ready.waiting))


# Given a list of Events, returns the index of the Event with the highest response ratio for the HRRN scheduler
def get_highest_rr(ready_queue, clock):
    highest_rr_index = 0
    highest_rr = ((clock - ready_queue[0].arrival) + ready_queue[0].service) / ready_queue[0].service

    for i in range(1, len(ready_queue)):
        if (((clock - ready_queue[i].arrival) + ready_queue[i].service) / ready_queue[i].service) > highest_rr:
            highest_rr = ((clock - ready_queue[i].arrival) + ready_queue[i].service) / ready_queue[i].service
            highest_rr_index = i
    return highest_rr_index


def output_metrics(completed, clock, ready_queue_length, num_processes, total_idle_time, arrival_rate, srate):
    sum2 = 0
    for i in range(num_processes):
        sum2 += completed[i].turnaround
    avg_tat = sum2 / num_processes

    avg_turnaround = num_processes / clock

    sum4 = 0
    for i in range(len(ready_queue_length)):
        sum4 += ready_queue_length[i]

    avg_processes = sum4 / len(ready_queue_length)

    cpu_util = (clock - total_idle_time) / clock

    metrics = [arrival_rate, srate, avg_tat, avg_turnaround, cpu_util, avg_processes]

    f = open('simdata.csv', 'a')
    for i in range(len(metrics)):
        f.write(str(metrics[i]))
        if i < len(metrics) - 1:
            f.write(',')
    f.write('\n')
    f.close()


"""
    Class Event: Holds needed information about simulated processes 
        Attributes:
            type: Indicates the type of event. Possible values: 'ARRIVAL','DEPARTURE','QUANTUM','COMPLETED','READY'
            arrival: Simulated arrival time of the process (seconds)
            service: Simulated service time of the process (seconds
            departure: Planned departure time for a process that is being serviced by the CPU (Given by clock time + service time)
            turnaround: Turnaround time for completed processes (Given by departure time - arrival time)
            waiting: Time a process has spent waiting to be serviced by CPU (clock time - arrival time)           
"""


class Event:
    def __init__(self, status, arrival, service, departure, turnaround, waiting):
        self.type = status
        self.arrival = arrival
        self.service = service
        self.departure = departure
        self.turnaround = turnaround
        self.waiting = waiting

    # event_time: Takes an Event object and returns the time that the event will occur based on the event type.
    def event_time(self):
        if self.type == 'ARRIVAL':
            return self.arrival
        elif self.type == 'DEPARTURE':
            return self.departure
        elif self.type == 'QUANTUM':
            return self.arrival
        else:
            return 0


"""
FCFS: Simulates the First Come First Served scheduling algorithm. 
    
        Events arrive at an average rate per second given by arrival_rate, and are placed into the ready_queue. 
        The simulated processes will be "serviced" by the CPU on a first come, first served basis. Completed processes 
        will be appended to a list of Events used for metrics, until a max number of processes defined by num_processes
        is reached. 
    
        Metrics computed: 
            Average turnaround time
            Total throughput (processes per second)
            Percentage of CPU utilization
            Average number of processes in the ready queue

Arguments:  arrival_rate (Rate per second of arriving processes)
            srate (Inverse of the average service time)
            num_processes (Number of processes to simulate)
    * arrival_rate and avg_service_time provided as command line arguments
"""


def fcfs(arrival_rate, srate, num_processes):
    # Initialization
    event_queue = []
    ready_queue = []
    completed = []
    ready_queue_length = []
    clock = 0
    idle = True
    total_processed = 0
    cpu_check_time = 0
    total_idle_time = 0

    # Generate first event
    first_event = Event('ARRIVAL', (gen_rand_time(arrival_rate)), gen_rand_time(srate), 0, 0, 0)
    event_queue.append(first_event)

    while total_processed < num_processes:
        next_event = event_queue[0]

        # Next event is an arrival:
        # Remove from event_queue, set clock, add to ready_queue
        # Generate next arrival and add to event_queue
        if next_event.type == 'ARRIVAL':
            clock = next_event.arrival
            event_queue.pop(0)
            ready_queue.append(next_event)
            ready_queue_length.append(len(ready_queue))

            # Generate next arrival
            new_event = Event('ARRIVAL', (gen_rand_time(arrival_rate) + clock), gen_rand_time(srate), 0, 0, 0)

            # Call insert_event to place event in correct location in event_queue
            insert_event(new_event, event_queue)

        # Next event in event_queue is a departure:
        # Remove from event queue, set clock, set CPU to idle again, increment # of processes completed
        # Append completed event to list
        if next_event.type == 'DEPARTURE':
            clock = next_event.departure
            event_queue.pop(0)
            idle = True
            cpu_check_time = clock
            total_processed += 1
            completed.append(Event('COMPLETED', next_event.arrival, next_event.service, next_event.departure,
                                   clock - next_event.arrival, next_event.waiting))

        # When CPU is idle and there is a process in ready_queue:
        # Remove process from ready_queue and schedule a departure event
        if idle is True and len(ready_queue) != 0:
            active_process = ready_queue[0]
            ready_queue.pop(0)
            idle = False
            total_idle_time += clock - cpu_check_time
            schedule_departure(active_process, event_queue, clock)

    output_metrics(completed, clock, ready_queue_length, num_processes, total_idle_time, arrival_rate, srate)

"""
    # Prints metrics to console, used for testing
    print("****FCFS****")
    print("# completed", len(completed))
    print("arrival_rate:", arrival_rate, "srate:", srate)
    print("Clock", clock)

    sum2 = 0
    for i in range(num_processes):
        sum2 += completed[i].turnaround
    print("AVG TAT", sum2 / 10000)

    sum3 = num_processes / clock
    print("total throughput", sum3)

    sum4 = 0
    for i in range(len(ready_queue_length)):
        sum4 += ready_queue_length[i]
    print("#", len(ready_queue_length), "AVG #processes in ready queue", sum4 / num_processes)

    sum5 = (clock - total_idle_time) / clock
    print("CPU UTIL%", sum5)

    # END FCFS
"""

"""
SRTF: Simulates the Shortest Time Remaining First scheduling algorithm. 
    
        Events arrive at an average rate per second given by arrival_rate, and are placed into the ready_queue. 
        The simulated processes will be "serviced" in an order based on the shortest remaining service time. This scheduler
        is preemptive, meaning new arrivals can take the place of the active process if their service time is shorter.
        
    
        Metrics computed: 
            Average turnaround time
            Total throughput (processes per second)
            Percentage of CPU utilization
            Average number of processes in the ready queue

Arguments:  arrival_rate (Rate per second of arriving processes)
            srate (Inverse of the average service time)
            num_processes (Number of processes to simulate)
    * arrival_rate and avg_service_time provided as command line arguments
"""


def srtf(arrival_rate, srate, num_processes):
    # Initialization
    event_queue = []
    ready_queue = []
    completed = []
    ready_queue_length = []
    clock = 0
    idle = True
    total_processed = 0
    departure_loc = 0
    cpu_check_time = 0
    total_idle_time = 0

    # Generate first event
    first_event = Event('ARRIVAL', (gen_rand_time(arrival_rate)), gen_rand_time(srate), 0, 0, 0)
    event_queue.append(first_event)

    while total_processed < num_processes:
        next_event = event_queue[0]

        # For SRTF: new arrivals can preempt the current process so that needs to be completed in this step
        if next_event.type == 'ARRIVAL':
            clock = next_event.arrival
            event_queue.pop(0)

            # Check for preemption
            # If there are no events scheduled, simply append to ready_queue
            if len(event_queue) == 0:
                insert_ordered_srtf(next_event, ready_queue, next_event.service)
                ready_queue_length.append(len(ready_queue))

            # Find out if the new arrival should preempt the current process
            else:

                # Find location of departure event in event_queue, if any
                for i in range(len(event_queue)):
                    if event_queue[i].type == 'DEPARTURE':
                        departure_loc = i

                # If service time of the new arrival is lower, remove departure from the event queue
                # and insert the process back into the ready queue with its remaining service time.
                # Then schedule a new departure for the new event.
                if next_event.service < event_queue[departure_loc].departure - clock:
                    old_process = event_queue[departure_loc]
                    event_queue.pop(departure_loc)
                    insert_ordered_srtf(old_process, ready_queue, old_process.departure - clock)
                    ready_queue_length.append(len(ready_queue))
                    schedule_departure(next_event, event_queue, clock)

                # If the service time of the new arrival is not lower than the scheduled departure,
                # insert new event into the ready queue
                else:
                    insert_ordered_srtf(next_event, ready_queue, next_event.service)
                    ready_queue_length.append(len(ready_queue))

            # Create and insert next planned arrival
            new_event = Event('ARRIVAL', (gen_rand_time(arrival_rate) + clock), gen_rand_time(srate), 0, 0, 0)
            insert_event(new_event, event_queue)

        # Functions the same as FCFS
        if next_event.type == 'DEPARTURE':
            clock = next_event.departure
            event_queue.pop(0)
            idle = True
            cpu_check_time = clock
            total_processed += 1
            completed.append(Event('COMPLETED', next_event.arrival, next_event.service, next_event.departure,
                                   clock - next_event.arrival, next_event.waiting))

        # Since the ready queue is sorted by remaining service time, the next process to be serviced can be found at
        # ready_queue[0]
        if idle is True and len(ready_queue) != 0:
            active_process = ready_queue[0]
            ready_queue.pop(0)
            idle = False
            total_idle_time += clock - cpu_check_time
            schedule_departure(active_process, event_queue, clock)

    output_metrics(completed, clock, ready_queue_length, num_processes, total_idle_time, arrival_rate, srate)


"""
HRRN: Simulates the Highest Response Ratio Next scheduling algorithm. 

        Events arrive at an average rate per second given by arrival_rate, and are placed into the ready_queue. 
        From the ready_queue, the next process to be serviced by the CPU is selected based on the highest response ratio
        given by (Waiting time + service time) / (service time). This scheduler is non preemptive.


        Metrics computed: 
            Average turnaround time
            Total throughput (processes per second)
            Percentage of CPU utilization
            Average number of processes in the ready queue

Arguments:  arrival_rate (Rate per second of arriving processes)
            srate (Inverse of the average service time)
            num_processes (Number of processes to simulate)
    * arrival_rate and avg_service_time provided as command line arguments
"""


def hrrn(arrival_rate, srate, num_processes):
    # Initialization
    event_queue = []
    ready_queue = []
    completed = []
    ready_queue_length = []
    clock = 0
    idle = True
    total_processed = 0
    cpu_check_time = 0
    total_idle_time = 0

    # Generate first event
    first_event = Event('ARRIVAL', (gen_rand_time(arrival_rate)), gen_rand_time(srate), 0, 0, 0)
    event_queue.append(first_event)

    while total_processed < num_processes:
        next_event = event_queue[0]

        # Process arrivals: HRRN ready_queue is not sorted so no special insertion logic is needed
        if next_event.type == 'ARRIVAL':
            clock = next_event.arrival
            event_queue.pop(0)
            ready_queue.append(next_event)
            ready_queue_length.append(len(ready_queue))

            new_event = Event('ARRIVAL', (gen_rand_time(arrival_rate) + clock), gen_rand_time(srate), 0, 0, 0)
            insert_event(new_event, event_queue)

        # Functions the same as FCFS
        if next_event.type == 'DEPARTURE':
            clock = next_event.departure
            event_queue.pop(0)
            idle = True
            cpu_check_time = clock
            total_processed += 1
            completed.append(Event('COMPLETED', next_event.arrival, next_event.service, next_event.departure,
                                   clock - next_event.arrival, next_event.waiting))

        # Calls highest_rr_index with the ready queue to find the process with the highest response ratio
        # then schedules a departure for that process
        if idle is True and len(ready_queue) != 0:
            highest_rr_index = get_highest_rr(ready_queue, clock)
            active_process = ready_queue[highest_rr_index]
            ready_queue.pop(highest_rr_index)
            idle = False
            total_idle_time += clock - cpu_check_time
            schedule_departure(active_process, event_queue, clock)

    output_metrics(completed, clock, ready_queue_length, num_processes, total_idle_time, arrival_rate, srate)


"""
RR: Simulates the Round Robin scheduling algorithm. 

        The Round Robin functions differently from the other schedulers. Processes are serviced on a first come, first
        served basis but at a regular interval given by the quantum parameter the current process will be preempted and 
        placed at the end of the ready queue. 
     
        Metrics computed: 
            Average turnaround time
            Total throughput (processes per second)
            Percentage of CPU utilization
            Average number of processes in the ready queue

Arguments:  arrival_rate (Rate per second of arriving processes)
            srate (Inverse of the average service time)
            num_processes (Number of processes to simulate)
            quantum (quantum length)
    * arrival_rate and avg_service_time provided as command line arguments
"""


def rr(arrival_rate, srate, num_processes, quantum):
    # Initialization
    event_queue = []
    ready_queue = []
    completed = []
    ready_queue_length = []
    clock = 0
    idle = True
    total_processed = 0
    cpu_check_time = 0
    total_idle_time = 0
    quantum_tracker = 0
    departure_loc = 0
    found_departure = False

    # Generate first event
    first_event = Event('ARRIVAL', (gen_rand_time(arrival_rate)), gen_rand_time(srate), 0, 0, 0)
    event_queue.append(first_event)

    # Add first quantum to event queue
    first_quantum = Event('QUANTUM', quantum, quantum, quantum + quantum, 0, 0)

    quantum_tracker += quantum
    insert_event_rr(first_quantum, event_queue)

    while total_processed < num_processes:
        next_event = event_queue[0]

        if next_event.type == 'ARRIVAL':
            clock = next_event.arrival
            event_queue.pop(0)
            ready_queue.append(next_event)
            ready_queue_length.append(len(ready_queue))

            new_event = Event('ARRIVAL', (gen_rand_time(arrival_rate) + clock), gen_rand_time(srate), 0, 0, 0)

            insert_event_rr(new_event, event_queue)

        # If next event is a Quantum:
        # Cancel the current departure event and put the process at the back of the ready queue,
        # then schedule a departure for the next process in the ready_queue
        if next_event.type == 'QUANTUM':
            clock = next_event.arrival
            event_queue.pop(0)

            # Track the current number of quantums that have passed and generate the next quantum event
            quantum_tracker += quantum
            next_quantum = Event('QUANTUM', quantum_tracker, quantum, quantum_tracker + quantum, 0, 0)
            insert_event_rr(next_quantum, event_queue)

            # Find location of departure event
            for i in range(len(event_queue)):
                if event_queue[i].type == 'DEPARTURE':
                    departure_loc = i
                    found_departure = True

            # If departure is found and there is another process in the ready queue, complete preemption steps
            # (re append the old process to the ready queue and schedule a new departure)
            if found_departure is True and len(ready_queue) != 0:
                old_process = event_queue[departure_loc]
                event_queue.pop(departure_loc)
                ready_queue.append(
                    Event('READY', old_process.arrival, old_process.departure - clock, old_process.departure,
                          old_process.turnaround, old_process.waiting))
                next_process = ready_queue[0]
                ready_queue.pop(0)
                schedule_departure(next_process, event_queue, clock)
                found_departure = False

            # If no departure event is found in the ready queue and there is a process waiting to be serviced,
            # Schedule a departure event for the waiting process
            elif found_departure is False and len(ready_queue) != 0:
                schedule_departure(ready_queue[0], event_queue, clock)
                ready_queue.pop(0)
                idle = False
                total_idle_time += clock - cpu_check_time

        # Functions the same as FCFS
        if next_event.type == 'DEPARTURE':
            clock = next_event.departure
            event_queue.pop(0)
            idle = True
            cpu_check_time = clock
            total_processed += 1
            completed.append(Event('COMPLETED', next_event.arrival, next_event.service, next_event.departure,
                                   clock - next_event.arrival, next_event.waiting))

        # If a process departs before the quantum is up, a new one will be scheduled.
        if idle is True and len(ready_queue) != 0:
            active_process = ready_queue[0]
            ready_queue.pop(0)
            idle = False
            total_idle_time += clock - cpu_check_time
            schedule_departure(active_process, event_queue, clock)

    output_metrics(completed, clock, ready_queue_length, num_processes, total_idle_time, arrival_rate, srate)


if __name__ == '__main__':
    main()


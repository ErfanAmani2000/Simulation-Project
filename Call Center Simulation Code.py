from scipy import stats
import random
import math
import pandas as pd
import numpy as np


def starting_state():
    # State variables declaration
    state = dict()
    state['Normal Queue'] = 0
    state['Special Queue'] = 0
    state['Normal CallBack Queue'] = 0
    state['Special CallBack Queue'] = 0
    state['Expert Server Status'] = 0
    state['Amateur Server Status'] = 0
    state['Technical Server Status'] = 0
    state['Special Technical Queue'] = 0
    state['Normal Technical Queue'] = 0
    state['Shift Status'] = 0

    # Data: will save every essential data
    data = dict()
    data['Users'] = dict()
    """ 
    Users dictionary is implemented to track each customer's entrance time, service start time, and service end time, 
    service technical start time, and service technical end time, for instance:{1:[22, 25, 29, null, null]}. It is
    noteworthy to mention that not all the users use technical service so the 4th and 5th elements of each list is set
    to null for initialization.
    """
    # The dictionary below is needed to store the last time for which each queue has changed in length.
    data['Last Time Queue Length Changed'] = dict()
    data['Last Time Queue Length Changed']['Normal Queue'] = 0
    data['Last Time Queue Length Changed']['Special Queue'] = 0
    data['Last Time Queue Length Changed']['Normal CallBack Queue'] = 0
    data['Last Time Queue Length Changed']['Special CallBack Queue'] = 0
    data['Last Time Queue Length Changed']['Normal Technical Queue'] = 0
    data['Last Time Queue Length Changed']['Special Technical Queue'] = 0

    # The dictionary below is needed to store all users in each queue
    data['Queue Users'] = dict()
    data['Queue Users']['Normal Queue'] = dict()
    data['Queue Users']['Special Queue'] = dict()
    data['Queue Users']['Normal CallBack Queue'] = dict()
    data['Queue Users']['Special CallBack Queue'] = dict()
    data['Queue Users']['Normal Technical Queue'] = dict()
    data['Queue Users']['Special Technical Queue'] = dict()

    # The dictionary below is needed to store the last length of each queue.
    data['Last Queue Length'] = dict()
    data['Last Queue Length']['Normal Queue'] = 0
    data['Last Queue Length']['Special Queue'] = 0
    data['Last Queue Length']['Normal CallBack Queue'] = 0
    data['Last Queue Length']['Special CallBack Queue'] = 0
    data['Last Queue Length']['Normal Technical Queue'] = 0
    data['Last Queue Length']['Special Technical Queue'] = 0

    # The dictionary below is needed to store the last time for which each server status has been changed.
    data['Last Time Server Status Changed'] = dict()
    data['Last Time Server Status Changed']['Expert'] = 0
    data['Last Time Server Status Changed']['Amateur'] = 0
    data['Last Time Server Status Changed']['Technical'] = 0

    # The dictionary below is needed to store the last server status.
    data['Last Server Status'] = dict()
    data['Last Server Status']['Expert'] = 0
    data['Last Server Status']['Amateur'] = 0
    data['Last Server Status']['Technical'] = 0

    # These crumb data are stored for the purpose that is obviously expressed.
    data['Last Time Disruption start'] = -1440
    data['Number Of No Waiting Special User'] = 0
    data['Users To waiting In Technical Queue'] = []
    data['Number of special users'] = 0

    # The dictionary below is needed to store the maximum length of each queue during the simulation.
    data['Maximum Queue Length'] = dict()
    data['Maximum Queue Length']['Normal Queue'] = 0
    data['Maximum Queue Length']['Special Queue'] = 0
    data['Maximum Queue Length']['Normal CallBack Queue'] = 0
    data['Maximum Queue Length']['Special CallBack Queue'] = 0
    data['Maximum Queue Length']['Normal Technical Queue'] = 0
    data['Maximum Queue Length']['Special Technical Queue'] = 0

    # The dictionary below is needed to store the maximum waiting time of users in each queue during the simulation.
    data['Maximum Waiting time'] = dict()
    data['Maximum Waiting time']['Normal Queue'] = 0
    data['Maximum Waiting time']['Special Queue'] = 0
    data['Maximum Waiting time']['Normal CallBack Queue'] = 0
    data['Maximum Waiting time']['Special CallBack Queue'] = 0
    data['Maximum Waiting time']['Normal Technical Queue'] = 0
    data['Maximum Waiting time']['Special Technical Queue'] = 0

    # Cumulative statistics that are necessary to assess the system performance measures.
    data['Cumulative Stats'] = dict()
    data['Cumulative Stats']['Special Users System Duration time'] = 0
    data['Cumulative Stats']['Number of Special Users with no Delay'] = 0
    data['Cumulative Stats']['Number of Special Users'] = 0

    # This specific dictionary in cumulative stats is assigned to store area under each queue length curve.
    data['Cumulative Stats']['Area Under Queue Length Curve'] = dict()
    data['Cumulative Stats']['Area Under Queue Length Curve']['Normal Queue'] = 0
    data['Cumulative Stats']['Area Under Queue Length Curve']['Special Queue'] = 0
    data['Cumulative Stats']['Area Under Queue Length Curve']['Normal CallBack Queue'] = 0
    data['Cumulative Stats']['Area Under Queue Length Curve']['Special CallBack Queue'] = 0
    data['Cumulative Stats']['Area Under Queue Length Curve']['Normal Technical Queue'] = 0
    data['Cumulative Stats']['Area Under Queue Length Curve']['Special Technical Queue'] = 0

    # This specific dictionary in cumulative stats is assigned to store area under waiting time for users in each queue.
    data['Cumulative Stats']['Area Under Waiting time'] = dict()
    data['Cumulative Stats']['Area Under Waiting time']['Normal Queue'] = 0
    data['Cumulative Stats']['Area Under Waiting time']['Special Queue'] = 0
    data['Cumulative Stats']['Area Under Waiting time']['Normal CallBack Queue'] = 0
    data['Cumulative Stats']['Area Under Waiting time']['Special CallBack Queue'] = 0
    data['Cumulative Stats']['Area Under Waiting time']['Normal Technical Queue'] = 0
    data['Cumulative Stats']['Area Under Waiting time']['Special Technical Queue'] = 0

    # This specific dictionary in cumulative stats is assigned to store area under each server busy time.
    data['Cumulative Stats']['Area Under Server Busy time'] = dict()
    data['Cumulative Stats']['Area Under Server Busy time']['Amateur'] = 0
    data['Cumulative Stats']['Area Under Server Busy time']['Expert'] = 0
    data['Cumulative Stats']['Area Under Server Busy time']['Technical'] = 0

    # FEL initialization, and Starting events that initialize the simulation
    future_event_list = list()
    future_event_list.append({'Event Type': 'Shift Start/End', 'Event Time': 0, 'User': ''})
    future_event_list.append({'Event Type': 'Disruption Start', 'Event Time': 0, 'User': ''})
    future_event_list.append({'Event Type': 'Month Change', 'Event Time': 0, 'User': ''})
    future_event_list.append({'Event Type': 'Call Start', 'Event Time': 0, 'User': [1, 'Special', 'Expert', 0]})
    return state, future_event_list, data


def fel_maker(future_event_list: list, event_type: str, clock: float, state: dict, user: list = None,
              disruption: str = 'No'):
    """
    This function is supposed to set the next event into future event list
    param future_event_list: list that contains all future events
    param event_type: types of each event that can occur in this simulation
    param clock: simulation clock
    param state: dictionary that contains all state variables
    param user: a list that filled with each user's attributes
    param disruption: whether the next event is set in disruption conditions or not
    """
    event_time = 0
    inter_arrival_param = {1: 3, 2: 1, 3: 2}
    disruption_inter_arrival_param = {1: 2, 2: 1 / 2, 3: 1}
    service_time_param = {"Amateur": 7, "Expert": 3}

    if event_type == 'Call Start':
        if disruption == 'No':  # if the system is not in the disruption condition ...
            event_time = clock + exponential(inter_arrival_param[state['Shift Status']])
        else:
            event_time = clock + exponential(disruption_inter_arrival_param[state['Shift Status']])

    elif event_type == 'Call End':
        event_time = clock + exponential(service_time_param[user[2]])

    elif event_type == 'Technical Call End':
        event_time = clock + exponential(10)

    elif event_type == 'Disruption Start':
        event_time = clock + 1440 * random.randint(1, 30)

    elif event_type == 'Month Change':
        event_time = clock + 30 * 1440

    elif event_type == 'Queue Quit':
        if user[1] == 'Normal':  # if a normal user want to quit from his/her queue ...
            event_time = clock + uniform(5, max(25, state['Normal Queue']))
        else:
            event_time = clock + uniform(5, max(25, state['Special Queue']))

    elif event_type == 'Shift Start/End':
        event_time = clock + 480

    new_event = {'Event Type': event_type, 'Event Time': event_time, 'User': user}
    future_event_list.append(new_event)


def exponential(beta: float) -> float:
    """
    param lambda_param: mean parameter of exponential distribution
    return: random variate that conforms to exponential distribution
    """
    r = random.random()
    return -beta * math.log(r)


def uniform(a: float, b: float) -> float:
    """
    param a: lower bound for uniform dist.
    param b: upper bound for uniform dist.
    return: random variate that obey uniform dist.
    """
    r = random.random()
    return a + (b - a) * r


def discrete_uniform(a: int, b: int) -> int:
    """
    param a: lower bound for discrete uniform dist.
    param b: upper bound for discrete uniform dist.
    return: random variate that obey discrete uniform dist.
    """
    r = random.random()
    for inc in range(a, b + 1):
        if (r < (inc + 1) / (b - a + 1)) and (r >= inc / (b - a + 1)):
            print(r)
            return inc


def data_server_calculater(data: dict, state: dict, clock: float, name: str):
    """
    This function is supposed to calculate area under each server busy time.
    param data: the dictionary that store every essential data
    param name: each server name, whether is expert, amateur or technical
    """
    data['Cumulative Stats']['Area Under Server Busy time'][name] += state['{} Server Status'.format(name)] \
                                                            * (clock - data['Last Time Server Status Changed'][name])
    data['Last Time Server Status Changed'][name] = clock


def data_queue_calculater(data: dict, state: dict, clock: float, name: str):
    """
    This function is supposed to calculate area under each queue length curve,
    and also the maximum queue length.
    """
    data['Cumulative Stats']['Area Under Queue Length Curve']['{} Queue'.format(name)] += state['{} Queue'.format(name)] \
                                                * (clock - data['Last Time Queue Length Changed']['{} Queue'.format(name)])
    data['Last Time Queue Length Changed']['{} Queue'.format(name)] = clock
    data['Maximum Queue Length']['{} Queue'.format(name)] = max(data['Maximum Queue Length']['{} Queue'.format(name)],
                                                                state['{} Queue'.format(name)])


def data_queue_user(data: dict, clock: float, name: str, user=None, technically='No', has_CallBack = 'No'):
    parameter = {"No": 1, "Yes": 3}  # to store clock in right position
    if clock != 'Exit':

        first_customer_in_queue = min(data['Queue Users']['{} Queue'.format(name)],
                                      key=data['Queue Users']['{} Queue'.format(name)].get)
        potential = data['Queue Users']['{} Queue'.format(name)][first_customer_in_queue][1]
        data['Users'][first_customer_in_queue][parameter[technically]] = clock
        data['Queue Users']['{} Queue'.format(name)].pop(first_customer_in_queue, None)
        if has_CallBack == 'Yes':
            data['Users'][first_customer_in_queue][6] = "it_is_CallBack"
        return first_customer_in_queue, potential
    else:
        data['Users'][user[0]][1] = clock
        data['Queue Users']['{} Queue'.format(name)].pop(user[0], None)
        return


def call_start(future_event_list: list, state: dict, clock: float, data: dict, user: list):
    """
    This function is supposed to implement call start event that is fully described in project's report.
    """
    data['Users'][user[0]] = [clock, -1, -1, None, None, user[1], None]  # -1 means that the user did not receive service

    if user[1] == 'Normal':  # if a normal user call ...
        if state['Amateur Server Status'] == 3:  # if all amateur server are busy ...
            if state['Expert Server Status'] < 2:  # if at least one expert server is free ...
                data['Last Server Status']['Expert'] = state['Expert Server Status']
                state['Expert Server Status'] += 1
                user[2] = 'Expert'

                data_server_calculater(data, state, clock, 'Expert')
                data['Users'][user[0]][1] = clock
                fel_maker(future_event_list, 'Call End', clock, state, [user[0], 'Normal', 'Expert', 0])

            else:  # if all expert servers are also busy at the time ...
                data['Last Queue Length']['Normal Queue'] = state['Normal Queue']
                state['Normal Queue'] += 1
                data['Queue Users']['Normal Queue'][user[0]] = [clock, 0]
                if state['Normal Queue'] >= 4:  # if normal queue length is more than 4 ...
                    if random.random() <= 0.5:  # according to historical data half of users will choose to use call-back option
                        data['Last Queue Length']['Normal Queue'] = state['Normal Queue']
                        state['Normal Queue'] -= 1
                        data['Queue Users']['Normal Queue'].pop(user[0], None)
                        data['Last Queue Length']['Normal Queue'] = state['Normal CallBack Queue']
                        state['Normal CallBack Queue'] += 1
                        data['Queue Users']['Normal CallBack Queue'][user[0]] = [clock, 0]
                        data_queue_calculater(data, state, clock, 'Normal CallBack')
                    else:  # users that did not use call-back option
                        if random.random() <= 0.15:  # according to historical data, 15% of them will choose to quit after some time
                            data['Queue Users']['Normal Queue'][user[0]] = [clock, 1]
                            fel_maker(future_event_list, 'Queue Quit', clock, state, user)

                    data_queue_calculater(data, state, clock, 'Normal')

        else:  # if at least one amateur server is free ...
            data['Last Server Status']['Amateur'] = state['Amateur Server Status']
            state['Amateur Server Status'] += 1
            user[2] = 'Amateur'

            data_server_calculater(data, state, clock, 'Amateur')
            data['Users'][user[0]][1] = clock
            fel_maker(future_event_list, 'Call End', clock, state, [user[0], 'Normal', 'Amateur', 0])

    else:  # if a special user call ...
        data['Number of special users'] += 1
        if state['Expert Server Status'] < 2:  # if at least one expert server is free ...
            data['Last Server Status']['Expert'] = state['Expert Server Status']
            state['Expert Server Status'] += 1
            user[2] = 'Expert'

            data_server_calculater(data, state, clock, 'Expert')
            data['Users'][user[0]][1] = clock
            data['Number Of No Waiting Special User'] += 1
            fel_maker(future_event_list, 'Call End', clock, state, [user[0], 'Special', 'Expert', 0])
        else:  # if all expert servers are busy ...
            data['Last Queue Length']['Special Queue'] = state['Special Queue']
            state['Special Queue'] += 1
            data['Queue Users']['Special Queue'][user[0]] = [clock, 0]
            if state['Special Queue'] >= 4:  # if special queue length is more than 4 ...
                if random.random() <= 0.5:  # according to historical data half of users will choose to use call-back option
                    data['Last Queue Length']['Special Queue'] = state['Special Queue']
                    state['Special Queue'] -= 1
                    data['Queue Users']['Special Queue'].pop(user[0], None)
                    data['Last Queue Length']['Special CallBack Queue'] = state['Special CallBack Queue']
                    state['Special CallBack Queue'] += 1
                    data['Queue Users']['Special CallBack Queue'][user[0]] = [clock, 0]
                    data_queue_calculater(data, state, clock, 'Special CallBack')
                else:  # users that did not use call-back option
                    if random.random() <= 0.15:  # according to historical data, 15% of them will choose to quit after some time
                        data['Queue Users']['Special Queue'][user[0]] = [clock, 1]
                        fel_maker(future_event_list, 'Queue Quit', clock, state, user)

                data_queue_calculater(data, state, clock, 'Special')
    new_user = [user[0] + 1, '', '', 0]
    if random.random() <= 0.3:  # according to data, 30% of users that call this call center are special
        new_user[1] = 'Special'
    else:
        new_user[1] = 'Normal'
    if clock >= data['Last Time Disruption start'] + 1440:  # whether next user should be scheduled in disruption condition or not
        fel_maker(future_event_list, 'Call Start', clock, state, new_user, disruption='No')
    else:
        fel_maker(future_event_list, 'Call Start', clock, state, new_user, disruption='Yes')


def call_end(future_event_list: list, state: dict, clock: float, data: dict, user: list):
    """
    This function is supposed to implement call end event that is fully described in project's report.
    """
    data['Users'][user[0]][2] = clock  # here we store user's call-end time in user's dictionary

    if random.random() < 0.15:  # according to historical data, 15% of users need technical advice
        if state['Technical Server Status'] == 2:  # if all technical users are busy at the time ...
            if user[1] == 'Normal':  # if a normal user wants to use technical advice ...
                data['Last Queue Length']['Normal Technical Queue'] = state['Normal Technical Queue']
                state['Normal Technical Queue'] += 1
                data['Queue Users']['Normal Technical Queue'][user[0]] = [clock, 0]

                data_queue_calculater(data, state, clock, 'Normal Technical')
                data['Users To waiting In Technical Queue'].append(user[0])

            elif user[1] == 'Special':  # if a special user wants to use technical advice ...
                data['Last Queue Length']['Special Technical Queue'] = state['Special Technical Queue']
                state['Special Technical Queue'] += 1
                data['Queue Users']['Special Technical Queue'][user[0]] = [clock, 0]

                data_queue_calculater(data, state, clock, 'Special Technical')
                data['Users To waiting In Technical Queue'].append(user[0])
        elif state['Technical Server Status'] < 2:  # if at least one technical server is free at the time ...
            data['Last Server Status']['Technical'] = state['Technical Server Status']
            state['Technical Server Status'] += 1

            data_server_calculater(data, state, clock, 'Technical')
            data['Users'][user[0]][3] = clock
            fel_maker(future_event_list, 'Technical Call End', clock, state, user)
    if user[2] == 'Expert':  # if the server that want to end his/her last call is expert ...
        if state['Special Queue'] > 0:  # whether the special queue is empty or not ...
            data['Last Queue Length']['Special Queue'] = state['Special Queue']
            state['Special Queue'] -= 1
            first_customer_in_queue, potential = data_queue_user(data, clock, 'Special')

            fel_maker(future_event_list, 'Call End', clock, state, [first_customer_in_queue, '', 'Expert', potential])
        else:  # if there is at least one person in the special queue ...
            if state['Normal Queue'] == 0:  # if normal user's queue is empty ...
                if (state['Shift Status'] == 2) or (
                        state['Shift Status'] == 3):  # if we are in 2nd or 3rd shift of a day
                    if state['Special CallBack Queue'] > 0:  # if special user's call-back queue is not empty ...
                        data['Last Queue Length']['Special CallBack Queue'] = state['Special CallBack Queue']
                        state['Special CallBack Queue'] -= 1
                        first_customer_in_queue, potential = data_queue_user(data, clock, 'Special CallBack', has_CallBack= "Yes")

                        data_queue_calculater(data, state, clock, 'Special CallBack')

                        fel_maker(future_event_list, 'Call End', clock, state, [first_customer_in_queue, "", 'Expert', potential])
                    else:  # if special user's call-back queue is empty ...
                        if state['Normal CallBack Queue'] > 0:  # whether normal user's call-back queue is not empty ...
                            data['Last Queue Length']['Normal CallBack Queue'] = state['Normal CallBack Queue']
                            state['Normal CallBack Queue'] -= 1

                            first_customer_in_queue, potential = data_queue_user(data, clock, 'Normal CallBack', has_CallBack= "Yes")
                            data_queue_calculater(data, state, clock, 'Normal CallBack')

                            fel_maker(future_event_list, 'Call End', clock, state,
                                      [first_customer_in_queue, "", 'Expert', potential])
                        else:  # normal user's call-back queue is empty too ...
                            data['Last Server Status']['Expert'] = state['Expert Server Status']
                            state['Expert Server Status'] -= 1
                            data_server_calculater(data, state, clock, 'Expert')
                else:  # if we are in the 1st shift of the day ...
                    data['Last Server Status']['Expert'] = state['Expert Server Status']
                    state['Expert Server Status'] -= 1
                    data_server_calculater(data, state, clock, 'Expert')
            elif state['Normal Queue'] > 0:  # whether normal user's queue is not empty ...
                data['Last Queue Length']['Normal Queue'] = state['Normal Queue']
                state['Normal Queue'] -= 1

                first_customer_in_queue, potential = data_queue_user(data, clock, 'Normal')
                data_queue_calculater(data, state, clock, 'Normal')

                fel_maker(future_event_list, 'Call End', clock, state,
                          [first_customer_in_queue, '', 'Expert', potential])

    elif user[2] == 'Amateur':  # if the server that want to end his/her last call is amateur ...
        if state['Normal Queue'] > 0:  # if normal user's queue is not empty ...
            data['Last Queue Length']['Normal Queue'] = state['Normal Queue']
            state['Normal Queue'] -= 1
            first_customer_in_queue, potential = data_queue_user(data, clock, 'Normal')
            data_queue_calculater(data, state, clock, 'Normal')
            fel_maker(future_event_list, 'Call End', clock, state, [first_customer_in_queue, '', 'Amateur', potential])
        elif state['Normal Queue'] == 0:  # if normal user's queue is empty ...
            if state['Shift Status'] == 2 or state['Shift Status'] == 3:  # if we are in 2nd or 3rd shift of a day
                if state['Normal CallBack Queue'] > 0:  # if special user's call-back queue is not empty at the moment ...
                    state['Normal CallBack Queue'] -= 1
                    first_customer_in_queue, potential = data_queue_user(data, clock, 'Normal CallBack', has_CallBack= "Yes")
                    data_queue_calculater(data, state, clock, 'Normal CallBack')
                    data['Users'][first_customer_in_queue][1] = clock
                    fel_maker(future_event_list, 'Call End', clock, state,
                              [first_customer_in_queue, "", 'Amateur', potential])
                else:  # if special user's call-back queue is empty at the moment ...
                    data['Last Server Status']['Amateur'] = state['Amateur Server Status']
                    state['Amateur Server Status'] -= 1
                    data_server_calculater(data, state, clock, 'Amateur')
            else:  # if we are in 1st shift of a day
                data['Last Server Status']['Amateur'] = state['Amateur Server Status']
                state['Amateur Server Status'] -= 1
                data_server_calculater(data, state, clock, 'Amateur')


def technical_call_end(future_event_list: list, state: dict, clock: float, data: dict, user: list):
    """
    This function is supposed to implement technical call end event that is fully described in project's report.
    It is important to mention that technical call start is planned in call end event.
    """
    data['Users'][user[0]][4] = clock  # here we store user's technical call-end time in user's dictionary
    if state['Special Technical Queue'] == 0:  # whether there is no special user in the technical queue ...
        if state['Normal Technical Queue'] == 0:  # if there is also no normal user in the technical queue ...
            data['Last Server Status']['Technical'] = state['Technical Server Status']
            state['Technical Server Status'] -= 1

        else:  # if there are at least one normal user in the technical queue ...
            data['Last Queue Length']['Normal Technical Queue'] = state['Normal Technical Queue']
            state['Normal Technical Queue'] -= 1
            first_customer_in_queue, potential = data_queue_user(data, clock, 'Normal Technical', technically="Yes")

            fel_maker(future_event_list, 'Technical Call End', clock, state,
                      [first_customer_in_queue, "", "", potential])
    else:  # whether there are at least one special user in the technical queue ...
        data['Last Queue Length']['Special Technical Queue'] = state['Special Technical Queue']
        state['Special Technical Queue'] -= 1
        first_customer_in_queue, potential = data_queue_user(data, clock, 'Special Technical', technically="Yes")

        fel_maker(future_event_list, 'Technical Call End', clock, state, [first_customer_in_queue, "", "", potential])


def disruption_start(clock: float, data: dict):
    """
    This function ganna store last time disruption occurred, and it's defined only to have one function for each event.
    """
    data['Last Time Disruption start'] = clock


def month_change(future_event_list: list, state: dict, clock: float):
    """
    This function is supposed to implement month change.
    """
    fel_maker(future_event_list, 'Disruption Start', clock, state, disruption='Yes')
    fel_maker(future_event_list, 'Month Change', clock, state)


def queue_quit(state: dict, user: list, data: dict):
    """
    This function is supposed to implement queue quit event for users that have potential to do so.
    """
    if data['Users'][user[0]][1] == -1:  # if it is !=-1 then mean of he start receiving service before quit of queue
        if user[1] == 'Normal':
            data['Last Queue Length']['Normal Queue'] = state['Normal Queue']
            state['Normal Queue'] -= 1
            data_queue_user(data, 'Exit', 'Normal', user)

        else:
            data['Number of special users'] -= 1
            data['Last Queue Length']['Special Queue'] = state['Special Queue']
            state['Special Queue'] -= 1
            data_queue_user(data, 'Exit', 'Special', user)


def shift_start_end(future_event_list: list, state: dict, clock: float):
    """
    This function is supposed to implement shift change.
    """
    if clock % 1440 < 480:  # if mod(clock, 1440) < 480, this means we are still in first shift
        state['Shift Status'] = 1
    elif (clock % 1440 >= 480) and (clock % 1440 < 960):  # if 480 < mod(clock, 1440) < 960, this means we are in second shift
        state['Shift Status'] = 2
    else:
        state['Shift Status'] = 3  # if none of the above, so we are in third shift
    fel_maker(future_event_list, 'Shift Start/End', clock, state)


def trace_maker(state: dict, clock: float, sorted_fel: list, trace_list: list, current_event: list):
    trace_data = list(state.values())
    trace_data.insert(0, round(clock, 3))
    trace_data.insert(0, current_event)

    fel_copy = sorted_fel.copy()

    while len(fel_copy) > 0:  # Filling trace with events of future event list
        trace_data.append(list(filter(None, fel_copy.pop(0).values())))
    trace_list.append(trace_data)


def simulation(simulation_time: float, trace_creator = False) -> dict:
    """
    This function is meant to do the simulation by help of introduced events.
    param simulation_time: this project is terminating simulation, so this parameter is simulation end time.
    return: data and state dictionary will be returned after one replication is done.
    """
    state, future_event_list, data = starting_state()
    clock = 0
    trace_list = []
    future_event_list.append({'Event Type': 'Shift Start/End', 'Event Time': simulation_time, 'User': ''})
    while clock < simulation_time:
        sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])
        current_event = sorted_fel[0]  # find imminent event
        clock = current_event['Event Time']  # advance time to current event time
        user = current_event['User']  # find the user of that event

        if trace_creator:
            trace_maker(state, clock, sorted_fel, trace_list, current_event)

        if clock < simulation_time:  # the if block below is ganna call proper event function for that event type
            if current_event['Event Type'] == 'Call Start':
                call_start(future_event_list, state, clock, data, user)
            elif current_event['Event Type'] == 'Call End':
                call_end(future_event_list, state, clock, data, user)
            elif current_event['Event Type'] == 'Technical Call End':
                technical_call_end(future_event_list, state, clock, data, user)
            elif current_event['Event Type'] == 'Disruption Start':
                disruption_start(clock, data)
            elif current_event['Event Type'] == 'Month Change':
                month_change(future_event_list, state, clock)
            elif current_event['Event Type'] == 'Queue Quit':
                queue_quit(state, user, data)
            elif current_event['Event Type'] == 'Shift Start/End':
                shift_start_end(future_event_list, state, clock)
            future_event_list.remove(current_event)

        else:  # if simulation time is passed after simulation end time, so FEL must be cleared
            future_event_list.clear()

    return data, state, trace_list


data, state, trace_list = simulation(30 * 24 * 60)


def calculate_kpi(data: dict, simulation_time: float) -> dict:
    """
    This function is meant to calculate all KPIs that described in project's report, then it stored them all
    in a dictionary called kpi_results
    return: kpi_results
    """
    kpi_results = dict()
    #
    kpi_results['Numbers'] = {}
    kpi_results['Numbers']['Special Queue'] = 0
    kpi_results['Numbers']['Normal Queue'] = 0
    kpi_results['Numbers']['Special Technical Queue'] = 0
    kpi_results['Numbers']['Normal Technical Queue'] = 0
    kpi_results['Numbers']['Special CallBack Queue'] = 0
    kpi_results['Numbers']['Normal CallBack Queue'] = 0
    #
    kpi_results['Max Queue Time'] = {}
    kpi_results['Max Queue Time']['Special Technical Queue'] = 0
    kpi_results['Max Queue Time']['Special Queue'] = 0
    kpi_results['Max Queue Time']['Normal Technical Queue'] = 0
    kpi_results['Max Queue Time']['Normal Queue'] = 0
    kpi_results['Max Queue Time']['Special CallBack Queue'] = 0
    kpi_results['Max Queue Time']['Normal CallBack Queue'] = 0
    #
    kpi_results['Average Queue Time'] = {}
    kpi_results['Average Queue Time']['Special Queue'] = 0
    kpi_results['Average Queue Time']['Normal Queue'] = 0
    kpi_results['Average Queue Time']['Special Technical Queue'] = 0
    kpi_results['Average Queue Time']['Normal Technical Queue'] = 0
    kpi_results['Average Queue Time']['Special CallBack Queue'] = 0
    kpi_results['Average Queue Time']['Normal CallBack Queue'] = 0

    for i in data['Users'].keys():
        if data['Users'][i][5] == "Special":
            if (data['Users'][i][2] != -1) and (data['Users'][i][1] != -1) and (data['Users'][i][1] != "Exit"):
                if (data['Users'][i][3] is None) and (data['Users'][i][4] is None):
                    if data['Users'][i][6] is None:
                        kpi_results['Average Queue Time']['Special Queue'] += data['Users'][i][1] - \
                                                                                           data['Users'][i][0]
                        kpi_results['Numbers']['Special Queue'] += 1
                        kpi_results['Max Queue Time']['Special Queue'] = \
                                            max(kpi_results['Max Queue Time']['Special Queue'], (data['Users'][i][1]-data['Users'][i][0]))
                    elif data['Users'][i][6] == 'it_is_CallBack':

                        kpi_results['Average Queue Time']['Special CallBack Queue'] += data['Users'][i][1] - \
                                                                                           data['Users'][i][0]
                        kpi_results['Numbers']['Special CallBack Queue'] += 1
                        kpi_results['Max Queue Time']['Special CallBack Queue'] = \
                                            max(kpi_results['Max Queue Time']['Special CallBack Queue'], (data['Users'][i][1]-data['Users'][i][0]))
                if (data['Users'][i][3] is not None) and (data['Users'][i][4] is not None):
                    if data['Users'][i][6] is None:
                        kpi_results['Average Queue Time']['Special Technical Queue'] += data['Users'][i][3] - data['Users'][i][2]
                        kpi_results['Numbers']['Special Technical Queue'] += 1
                        kpi_results['Max Queue Time']['Special Technical Queue'] = \
                                            max(kpi_results['Max Queue Time']['Special Technical Queue'], (data['Users'][i][3]-data['Users'][i][2]))
                    elif data['Users'][i][6] == 'it_is_CallBack':
                        kpi_results['Average Queue Time']['Special CallBack Queue'] += data['Users'][i][1] - \
                                                                                           data['Users'][i][0]
                        kpi_results['Numbers']['Special CallBack Queue'] += 1
                        kpi_results['Max Queue Time']['Special CallBack Queue'] = \
                                            max(kpi_results['Max Queue Time']['Special CallBack Queue'], (data['Users'][i][1]-data['Users'][i][0]))

        if data['Users'][i][5] == "Normal":
            if (data['Users'][i][2] != -1) and (data['Users'][i][1] != -1) and (data['Users'][i][1] != "Exit"):
                if (data['Users'][i][3] is None) and (data['Users'][i][4] is None):
                    if data['Users'][i][6] is None:
                        kpi_results['Average Queue Time']['Normal Queue'] += data['Users'][i][1] - \
                                                                                          data['Users'][i][0]
                        kpi_results['Numbers']['Normal Queue'] += 1
                        kpi_results['Max Queue Time']['Normal Queue'] = \
                                            max(kpi_results['Max Queue Time']['Normal Queue'], (data['Users'][i][1]-data['Users'][i][0]))
                    elif data['Users'][i][6] == 'it_is_CallBack':
                        kpi_results['Average Queue Time']['Normal CallBack Queue'] += data['Users'][i][1] - \
                                                                                           data['Users'][i][0]
                        kpi_results['Numbers']['Normal CallBack Queue'] += 1
                        kpi_results['Max Queue Time']['Normal CallBack Queue'] = \
                                            max(kpi_results['Max Queue Time']['Normal CallBack Queue'], (data['Users'][i][1]-data['Users'][i][0]))
                if (data['Users'][i][3] is not None) and (data['Users'][i][4] is not None):
                    if data['Users'][i][6] is None:
                        kpi_results['Average Queue Time']['Normal Technical Queue'] += data['Users'][i][3] - data['Users'][i][2]
                        kpi_results['Numbers']['Normal Technical Queue'] += 1
                        kpi_results['Max Queue Time']['Normal Technical Queue'] = \
                                            max(kpi_results['Max Queue Time']['Normal Technical Queue'], (data['Users'][i][3]-data['Users'][i][2]))
                    elif data['Users'][i][6] == 'it_is_CallBack':
                        kpi_results['Average Queue Time']['Normal CallBack Queue'] += data['Users'][i][1] - \
                                                                                           data['Users'][i][0]
                        kpi_results['Numbers']['Normal CallBack Queue'] += 1
                        kpi_results['Max Queue Time']['Normal CallBack Queue'] = \
                                            max(kpi_results['Max Queue Time']['Normal CallBack Queue'], (data['Users'][i][1]-data['Users'][i][0]))
    kpi_results['Average Queue Time']['Special Queue'] = kpi_results['Average Queue Time']['Special Queue'] / \
                                                                      kpi_results['Numbers']['Special Queue']
    kpi_results['Average Queue Time']['Normal Queue'] = kpi_results['Average Queue Time']['Normal Queue'] / \
                                                                     kpi_results['Numbers']['Normal Queue']
    kpi_results['Average Queue Time']['Special Technical Queue'] = kpi_results['Average Queue Time']['Special Technical Queue'] / \
                                                             kpi_results['Numbers']['Special Technical Queue']
    kpi_results['Average Queue Time']['Normal Technical Queue'] = kpi_results['Average Queue Time']['Normal Technical Queue'] / \
                                                            kpi_results['Numbers']['Normal Technical Queue']
    kpi_results['Average Queue Time']['Special CallBack Queue'] = kpi_results['Average Queue Time']['Special CallBack Queue'] / \
                                                             kpi_results['Numbers']['Special CallBack Queue']
    kpi_results['Average Queue Time']['Normal CallBack Queue'] = kpi_results['Average Queue Time']['Normal CallBack Queue'] / \
                                                            kpi_results['Numbers']['Normal CallBack Queue']
    server_number = {"Amateur": 3, "Expert": 2, "Technical": 2}
    kpi_results['Special Users time in system duration'] = 0
    kpi_results['number of Special Users in system with no waiting'] = 0
    for i in data['Users'].keys():
        if data['Users'][i][5] == "Special":
            if (data['Users'][i][2] != -1) and (data['Users'][i][1] != -1) and (data['Users'][i][1] != "Exit"):
                if (data['Users'][i][3] is None) and (data['Users'][i][4] is None):
                    kpi_results['Special Users time in system duration'] += data['Users'][i][2] - data['Users'][i][0]
                    if (data['Users'][i][1] - data['Users'][i][0]) == 0:
                        kpi_results['number of Special Users in system with no waiting'] += 1
                elif (data['Users'][i][3] is not None) and (data['Users'][i][4] is not None):
                    kpi_results['Special Users time in system duration'] += data['Users'][i][4] - data['Users'][i][0]
                    if (data['Users'][i][3] - data['Users'][i][2] == 0) and (
                            data['Users'][i][1] - data['Users'][i][0] == 0):
                        kpi_results['number of Special Users in system with no waiting'] += 1

    kpi_results['Special Users time in system duration'] = kpi_results['Special Users time in system duration'] / \
                    (kpi_results['Numbers']['Special Technical Queue'] + kpi_results['Numbers']['Special Queue'])
    kpi_results['number of Special Users in system with no waiting'] = kpi_results['number of Special Users in system with no waiting'] / \
                    (kpi_results['Numbers']['Special Technical Queue'] + kpi_results['Numbers']['Special Queue'])

    kpi_results['Average Queue Length'] = {}
    for i in data['Cumulative Stats']['Area Under Queue Length Curve'].keys():
        kpi_results['Average Queue Length'][i] = data['Cumulative Stats']['Area Under Queue Length Curve'][i] / simulation_time

    kpi_results['Max Queue Length'] = {}
    for i in data['Maximum Queue Length'].keys():
        kpi_results['Max Queue Length'][i] = data['Maximum Queue Length'][i]

    kpi_results['Server Utilization'] = {}
    for i in data['Cumulative Stats']['Area Under Server Busy time'].keys():
        kpi_results['Server Utilization'][i] = data['Cumulative Stats']['Area Under Server Busy time'][i] / \
                                               (simulation_time * server_number[i])

    return kpi_results


def trace_excel_maker(trace_list: list):
    """

    param trace_list:
    return:
    """
    trace = pd.DataFrame(trace_list)

    columns = list(state.keys())
    columns.insert(0, 'Clock')
    columns.insert(1, 'Current Event')

    columns.extend([f'fel{i}' for i in range(1, trace.shape[1] - 11)])  # to add future event list to trace dataframe
    trace = pd.DataFrame(trace_list, columns=columns)
    trace.to_excel('C:/Users/Lenovo/Desktop/trace_dataframe.xlsx', engine='xlsxwriter')


def calculate_kpi_estimation(replication: int, alpha = 0.05):
    kpi_result_data = {'Average Queue Length': {'Normal Queue': [],
                                                'Special Queue': [],
                                                'Normal CallBack Queue': [],
                                                'Special CallBack Queue': [],
                                                'Normal Technical Queue': [],
                                                'Special Technical Queue': []},
                       'Max Queue Length': {'Normal Queue': [],
                                            'Special Queue': [],
                                            'Normal CallBack Queue': [],
                                            'Special CallBack Queue': [],
                                            'Normal Technical Queue': [],
                                            'Special Technical Queue': []},
                       'Average Queue Time': {'Normal Queue': [],
                                              'Special Queue': [],
                                              'Normal CallBack Queue': [],
                                              'Special CallBack Queue': [],
                                              'Normal Technical Queue': [],
                                              'Special Technical Queue': []},
                       'Max Queue Time': {'Normal Queue': [],
                                          'Special Queue': [],
                                          'Normal CallBack Queue': [],
                                          'Special CallBack Queue': [],
                                          'Normal Technical Queue': [],
                                          'Special Technical Queue': []},
                       'Server Utilization': {'Amateur': [], 'Expert': [], 'Technical': []},
                       'Special Users time in system duration': [],
                       'Number of Special users in system with no waiting': []}

    kpi_result_estimation = {'Average Queue Length': {'Normal Queue': [],
                                                      'Special Queue': [],
                                                      'Normal CallBack Queue': [],
                                                      'Special CallBack Queue': [],
                                                      'Normal Technical Queue': [],
                                                      'Special Technical Queue': []},
                       'Max Queue Length': {'Normal Queue': [],
                                            'Special Queue': [],
                                            'Normal CallBack Queue': [],
                                            'Special CallBack Queue': [],
                                            'Normal Technical Queue': [],
                                            'Special Technical Queue': []},
                       'Average Queue Time': {'Normal Queue': [],
                                              'Special Queue': [],
                                              'Normal CallBack Queue': [],
                                              'Special CallBack Queue': [],
                                              'Normal Technical Queue': [],
                                              'Special Technical Queue': []},
                       'Max Queue Time': {'Normal Queue': [],
                                          'Special Queue': [],
                                          'Normal CallBack Queue': [],
                                          'Special CallBack Queue': [],
                                          'Normal Technical Queue': [],
                                          'Special Technical Queue': []},
                       'Server Utilization': {'Amateur': [], 'Expert': [], 'Technical': []},
                       'Special Users time in system duration': [],
                       'Number of Special users in system with no waiting': []}

    for r in range(replication):
        data = simulation(30 * 24 * 60)[0]
        kpi_result = calculate_kpi(data, 30 * 24 * 60)

        for i in kpi_result_data.keys():
            if (kpi_result_data[i] != 'Special Users time in system duration') and (kpi_result_data[i] != 'Number of Special users in system with no waiting'):
                for j in kpi_result_data[i]:
                    kpi_result_data[i][j].append(kpi_result[i][j])
            else:
                kpi_result_data[i].append(kpi_result[i])

    for i in kpi_result_data.keys():
        if (kpi_result_data[i] != 'Special Users time in system duration') and (kpi_result_data[i] != 'Number of Special users in system with no waiting'):
            for j in kpi_result_data[i]:
                kpi_result_estimation[i][j].append(np.mean(kpi_result_data[i][j]))
                kpi_result_estimation[i][j].append(np.mean(kpi_result_data[i][j]) - np.std(kpi_result_data[i][j]) / replication * stats.t.ppf(1 - alpha / 2, replication - 1))
                kpi_result_estimation[i][j].append(np.mean(kpi_result_data[i][j]) + np.std(kpi_result_data[i][j]) / replication * stats.t.ppf(1 - alpha / 2, replication - 1))
        else:
            kpi_result_estimation[i].append(np.mean(kpi_result_data[i]))
            kpi_result_estimation[i].append(np.mean(kpi_result_data[i]) - np.std(kpi_result_data[i]) / replication * stats.t.ppf(1 - alpha / 2, replication - 1))
            kpi_result_estimation[i].append(np.mean(kpi_result_data[i]) + np.std(kpi_result_data[i]) / replication * stats.t.ppf(1 - alpha / 2, replication - 1))

    return kpi_result_estimation


print(calculate_kpi_estimation(10))

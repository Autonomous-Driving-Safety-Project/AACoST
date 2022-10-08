#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re
import json
from subprocess import Popen, PIPE
from oscgen import OSCGen
import time

# predefinition
result_nums = 1000
cars = 'asp/cars-exp2.lp'
road = 'asp/road.lp'
task = 'asp/task.lp'
show = 'asp/show.lp'


cmd = 'clingo ' + str(result_nums) + ' asp/goal.lp asp/model.lp asp/maneuvers.lp '

result_obj = None


# run clingo to compute a plan
if __name__ == '__main__':
    plans_list = []
    result_arr = []
    cmd += cars + ' ' + road + ' ' + task + ' ' + show

    # get cars list
    if not os.path.exists(cars):
        raise TypeError(cars + ' does not exist')
    cars_text = open(cars).read()
    cars_list = re.findall(r'is_car\((\S*?)\)\.', cars_text)
    cars_list = ';'.join(cars_list)
    cars_list = cars_list.split(';')
    print(cars_list)

    # run cmd
    time_start = time.time()
    output = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)

    out, err = output.communicate()
    out = out.decode('utf-8')
    err = err.decode('utf-8')

    # print out
    # print err
    # print result
    if err.find("EEEOR") != -1:
        print(err)
        exit(1)
    else:
        if out.find("UNSATISFIABLE") != -1:
            print("no solution.")
            exit(2)
        else:
            answer = out.find("Answer: ")
            end = out.find("SATISFIABLE")
            result = out[answer:end - 1]
            plans_list = result.split('\n')[1::2]
            # print(plan)
    plan_index = 0
    for plan in plans_list:
        plan_index += 1

        osc = OSCGen('resources/xosc/template.xosc', 20, 50)
        osc_ego = OSCGen('resources/xosc/template.xosc', 20, 50)

        # print(plan)
        plan_result = []
        final_t = int(re.search(r'goal\(\S*?,(\d+)\)', plan).group(1))
        # print(final_t)
        for t in range(final_t + 1):
            t_result = []
            for car in cars_list:
                position = int(re.search(r'h\(position\(' + car + ',(-?\d+)\),' + str(t) + '\)', plan).group(1))
                speed = int(re.search(r'h\(speed\(' + car + ',(-?\d+)\),' + str(t) + '\)', plan).group(1))
                lane = int(re.search(r'h\(on\(' + car + ',(\d+)\),' + str(t) + '\)', plan).group(1))
                offset = re.search(r'h\(offset\(' + car + ',(\S*?)\),' + str(t) + '\)', plan).group(1)
                maneuver = re.findall(r'occurs\((\S*?),' + car + ',' + str(t) + '\)', plan)
                # print(car, t, position, speed, lane, offset, maneuver)

                if t == 0:
                    # add car
                    osc.add_entity(car, 'car_red' if car == 'ego' else 'car_white', position, -lane, speed)
                    osc_ego.add_entity(car, 'car_red' if car == 'ego' else 'car_white', position, -lane, speed)
                else:
                    # add maneuver
                    for m in maneuver:
                        if m != 'keep_lane' and m != 'keep_speed':
                            if car != 'ego':
                                osc.add_maneuver(car, m, t)
                            osc_ego.add_maneuver(car, m, t)

                t_result.append({
                    'car': car,
                    'state': {
                        'position': position,
                        'speed': speed,
                        'lane': lane,
                        'offset': offset
                    },
                    'maneuver': maneuver
                })
            plan_result.append(t_result)
        result_arr.append(plan_result)
        osc.add_global_parameter('exec_time', final_t, 'double')
        osc_ego.add_global_parameter('exec_time', final_t, 'double')
        osc.write('output/' + str(plan_index) + '.xosc')
        osc_ego.write('output/' + str(plan_index) + '-ego.xosc')
    result_obj = {
        'cars': cars_list,
        'plans': result_arr
    }
    time_end=time.time()
    print('time cost',time_end-time_start,'s')

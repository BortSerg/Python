import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button, CheckButtons
import datetime

import numpy as np

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)


def parse_date_time():
    data = open("/home/user/Log/fluke.log", 'r').read()
    x_list = []
    y_list = []
    mid_current = 0
    count = 0
    line_data = data.split("\n")
    for idx, line in enumerate(line_data):
        if line == '':
            break
        else:
            count += 1
            line = line.split(",")
            date_time_line = line[0]
            date_current_line = line[1]

            date_string, time_string = date_time_line.split(';')
            timestamp = datetime.datetime.strptime(date_string + " " + time_string, '%Y-%m-%d %H:%M:%S:%f')
            current, degree = date_current_line.split('E')
            current = float(current) * 1000
            #current = float(current) * (10**float(degree))
            if idx > 0:
                mid_current = (mid_current + current)/2
            x_list.append(timestamp)
            y_list.append(current)
    return x_list, y_list, mid_current


def animate(i):
        x_list, y_list, mid = parse_date_time()

        ax.clear()
        #ax.set_ylim([0, (0.600 * (10 ** -3))])
        ax.plot(x_list, y_list)
        plt.xlabel('Time')
        plt.ylabel('Current µA')
        plt.title('Fluke log %.2f µA' %mid)


ani = animation.FuncAnimation(fig, animate, interval=1000)

plt.show()



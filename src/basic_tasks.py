"""!
@file basic_tasks.py
    This file reads the MMA845x accelerometer and prints the X-axis reading
    every 500 ms.

@author Eric Qian, Callan Hill, Tommy Xu, JR Ridgely
@date   2023-Feb-16
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2.
"""
import gc
import pyb
import machine
import cotask
import task_share
import sys
import utime
import mma845x
import mlx_cam



def task1_fun(shares):
    """!
    Task which reads accelerometer's x value and puts in queue.
    @param shares A list holding the share and queue used by this task
    """
    # Get references to the share and queue which have been passed to this task
    _my_share, my_queue = shares
    mma = mlx_cam.MLX_Cam(machine.I2C (1),0x33)
    while True:
        if not my_queue.full ():
            my_queue.put(mma.get_image)           # Put data in queue
        yield 0


def task2_fun(shares):
    """!
    Task which prints the x value from the queue.
    @param shares A tuple of a share and queue from which this task gets data
    """
    # Get references to the share and queue which have been passed to this task
    _the_share, the_queue = shares

    while True:
        if the_queue.any ():
            print(the_queue.get ().v_ir)                     # Get data from queue
        yield 0


# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")

    # Create a share and a queue to test function and diagnostic printouts
    share0 = task_share.Share('h', thread_protect=False, name="Share 0")
    # Create a queue with 16 elements, each of which is a float
    q0 = task_share.Queue('f', 16, thread_protect=False, overwrite=False,
                          name="Queue 0")

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and se t trace to False when it's not needed
    task1 = cotask.Task(task1_fun, name="Task_1", priority=1, period=500,
                        profile=True, trace=False, shares=(share0, q0))
    task2 = cotask.Task(task2_fun, name="Task_2", priority=1, period=500,
                        profile=True, trace=False, shares=(share0, q0))
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break

    # Print a table of task data and a table of shared information data
    print('\n' + str (cotask.task_list))
    print(task_share.show_all())
    print(task1.get_trace())
    print('')


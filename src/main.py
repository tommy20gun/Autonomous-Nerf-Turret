"""!
@file main.py
This file contains the competition code for the turret.
It scans for a valid object using the IR sensor, controls
the turret to point at the object, and fires the turret.

@author Eric Qian, Callan Hill, Tommy Xu
"""
import pyb
import mlx_cam
import time
import machine
from servodriver import ServoDriver
from motordriver import MotorDriver
from encoder import EncoderReader
from controller import Controller
from fakeservo import FakeServo

def highpass(val):
    """! Return 1 if the value is greater than the minimum value, 0 otherwise.
    @param val The value to check.
    @return 1 if the value is greater than the minimum value, 0 otherwise.
    """
    min_val = 10
    if abs(val) > min_val:
        return 1
    else:
        return 0

def find_hotspots(arr):
    """! Find the location of the most clustered True values in a 2D array.
    @param arr The 2D array to search.
    @return The (row, col) location of the most clustered True values.
    """
    max_count = 0
    max_row, max_col = None, None
    # Search X values
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if arr[i][j]:
                # Count the number of True values clustered together
                count = 1
                # Traverse row until encountering False.
                for k in range(i+1, len(arr)):
                    if not arr[k][j]:
                        break
                    count += 1
                # Traverse col until encountering False.
                for k in range(j+1, len(arr[i])):
                    if not arr[i][k]:
                        break
                    count += 1
                # Traverse row left until encountering False.
                for k in range(i, 0, -1):
                    if not arr[k][j]:
                        break
                    count += 1
                # Traverse col left until encountering False.
                for k in range(j, 0, -1):
                    if not arr[i][k]:
                        break
                    count += 1
                
                # Update the target location if this is the most clustered value.
                if count > max_count:
                    max_count = count
                    max_row, max_col = i, j
    
    return max_row, max_col

def find_center(arr):
    """! Find the center of the True values in a 2D array.
    @param arr The 2D array to search.
    @return The (row, col) location of the center of the True values.
    """
    rows = len(arr)
    cols = len(arr[0])
    count = 0
    x_sum = 0
    y_sum = 0
    # Search x values
    for i in range(rows):
        # Search y values
        for j in range(cols):
            if arr[i][j]:
                # Add sum to count
                count += 1
                x_sum += i
                y_sum += j
    
    if count == 0:
        return None
    # Return average
    return (int(x_sum/count), int(y_sum/count))

def print_2d_array(arr):
    """! Print a 2D array in a grid format.
    @param arr The 2D array to print.
    """
    # determine the width of the largest element in the array
    max_width = max([len(str(elem)) for row in arr for elem in row])
    max_width = 2 if max_width <= 1 else max_width
    
    # print the top row of x indices
    print(" " * (max_width + 2), end="")
    for x in range(len(arr[0])):
        print(f"{x:{max_width}} ", end="")
    print()
    
    # print the rest of the grid with y indices
    for y, row in enumerate(arr):
        print(f"{y:{max_width}}| ", end="")
        for elem in row:
            print(f"{elem:{max_width}} ", end="")
        print()


def pixel_to_deg(x_val, y_val, x_max, y_max, x_fov, y_fov):
    """! Convert a pixel location to a degree location.
    @param x_val The x value of the pixel.
    @param y_val The y value of the pixel.
    @param x_max The maximum x value of the pixel.
    @param y_max The maximum y value of the pixel.
    @param x_fov The x field of view of the camera.
    @param y_fov The y field of view of the camera."""
    x_midpoint = x_max // 2
    y_midpoint = y_max // 2
    x_deg = (float(x_val - x_midpoint)/x_max) * x_fov
    y_deg = (float(y_val - y_midpoint)/y_max) * y_fov
    return int(x_deg), int(y_deg)

if __name__ == "__main__":
    """! Main competition code.
    This code runs the main competition code that adheres to the rules of the competition.
    It instantiates all relevant objects and runs the main loop, and controls the pan and tilt.
    It also controls the motor and fire control."""
    cam = mlx_cam.MLX_Cam(machine.I2C (1)) # MLX90640 camera
    servo = ServoDriver(pyb.Pin.board.PC6, 3, pyb.Pin.AF2_TIM3) # Servo driver
    target_ind = pyb.Pin(pyb.Pin.board.PC3, pyb.Pin.OUT_PP) # target indicator
    moe = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5) # motor driver
    moe.set_duty_cycle(0)
    encoder = EncoderReader(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4, 2) # encoder reader
    fakeservo = FakeServo() # fake servo
    kP = float(0.02) # proportional gain
    initialSetPoint = float(-1000) # initial set point
    controller = Controller(kP, initialSetPoint) # controller
    fire_control = pyb.Pin(pyb.Pin.board.PB3, pyb.Pin.OUT_PP) # fire control pin
    # Set fire control to off
    fire_control.low()
    # Set target indicator to off
    target_ind.low()
    # Reset servo location to default.
    servo.set_degree(210)
    time.sleep(2)
    avg_width = 4 # average width of target
    avg_height = 4 # average height of target
    valid_duration = 0 # duration of valid target
    valid_threshold = 2 # threshold for valid target
    fire_once = True # whether or not to fire only once
    ir_threshold = -37 # threshold for IR value
    prev_x, prev_y = -1, -1 # previous target location
    threshold_x, threshold_y = 3, 3 # threshold for target location
    y_ratio = 1.30 # y ratio for kinematic control
    x_ratio = 1.30 # x ratio for kinematic control
    total_size = cam._width * cam._height # total pixel size of camera
    avg_heatmap = [ [0] * (cam._width) for i in range(cam._height) ]
    raw_heatmap = [ [0] * (cam._width) for i in range(cam._height) ]
    target_y, target_x = 0,0
    binary_heatmap = avg_heatmap # initialize binary heatmap
    fakeservo.run(-180) # rotate 180
    fakeservo.reset() # reset zero'd position as 0.
    while True:
        # Set fire mode to off
        fire_control.low()
        # get image from camera
        image = list(cam.get_image())
        x = 0
        y = 0
        pix = 0
        # avg_heatmap = [[]] # initialize 2D array
        print(avg_heatmap)
        "image_2=list((cam.get_csv(image)))"
        # Find initial tilt point.
        for row in range(cam._height - avg_height):
            for col in range(cam._width - avg_width):
                total_val = 0
                for i in range(row, row + avg_height):
                    for k in range(col, col + avg_width):
                        total_val += image[i * cam._width + (cam._width - k - 1)]
                avg_heatmap[row][col] = total_val
                if total_val < pix:
                    pix = total_val
                    #print(row)
                    x = row
                    y = col
                #if image[row * cam._width + (cam._width - col - 1)] > pix:
                #    pix = image[row * cam._width + (cam._width - col - 1)]
                #    x = row
                #    y = col
        print(pix,x,y)
        servo.set_degree(210-y)
        # cam.ascii_art(image)
        # print(image)
        #print('\n'.join(' '.join(str(x) for x in row) for row in raw_heatmap)) # print heatmap as
        # Binarize heatmap.
        avg_val = total_val // total_size
        # Filter out noise with highpass filter.
        for i in range(len(raw_heatmap)):
            for j in range(len(raw_heatmap[i])):
                binary_heatmap[i][j] = highpass(raw_heatmap[i][j], ir_threshold if avg_val < ir_threshold else avg_val)
        print_2d_array(binary_heatmap)
        #print('\n'.join(' '.join(str(x) for x in row) for row in binary_heatmap))
        # Reset valid duration if no valid target. Otherwise, increment valid duration. If valid duration is greater than
        # threshold, then target is valid.
        if not any(1 in row for row in binary_heatmap):
            print("WARNING: NO VALID TARGET")
            target_ind.low()
            valid_duration = 0 # reset valid time
        else:
            target_ind.high()
            target_y, target_x = find_hotspots(binary_heatmap)
            print(f"X: {target_x} Y: {target_y}")
            if (valid_duration == 0 or (abs(prev_x-target_x < threshold_x) and abs(prev_y-target_y < threshold_y))):
                prev_x = target_x
                prev_y = target_y
                print("VALID")
                valid_duration += 1
            else:
                print("INVALID")
                valid_duration = 0
                prev_x = -1
                prev_y = -1
        print(f"average val: {avg_val}")
        #print(binary_heatmap) # print binary heatmap
        # Manually trigger garbage collection to avoid framentation.
        del(image)
        gc.collect()
        print(f"FC: {valid_duration} of {valid_threshold}")
        x_deg, y_deg = pixel_to_deg(target_x, target_y, cam._width, cam._height, 55, 35)
        print(f"X_DEGREE: {x_deg}, Y_DEGREE: {y_deg}")
        # Set tilt.
        servo.set_degree(210-int(y_deg * y_ratio))
        #servo.set_degree(230-target_y * y_ratio)
        # Set pan.
        fakeservo.run(-(int(target_x * x_ratio) - 17))
        # If valid duration is greater than threshold, then target is valid. Fire control is enabled.
        # And reset back to original position.
        if (valid_duration >= valid_threshold):
            # OK TO FIRE
            # Set tilt.
            print("FC: INIT")
            time.sleep(1)
            print("FC: FIRE ENABLE")
            fire_control.high()
            time.sleep(10)
            valid_duration = 0
            fakeservo.run(0)
            fakeservo.run(180)
            if fire_once:
                print("FC: FIRE ONCE FLAG ON. SHUT DOWN.")
                sys.exit(0)
        #print('\n\n\n')
    

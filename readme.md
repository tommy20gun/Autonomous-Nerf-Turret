# McIver Autonomous Nerf Blaster

<img src="https://github.com/EnumC/me405/blob/main/final/res/title.jpg.jpg?raw=true" width="500">

#  Introduction

It is our honor to introduce the Mciver Autonomous Nerf Turret. The software documentation can be found [here](https://enumc.github.io/me405/final/docs/html/)

click [here](https://drive.google.com/file/d/1yIYNy-2PuTGBKp5YCygmx9BtBqGw15uQ/view?usp=sharing) for a video demonstration of the Nerf Turret.

![gun photo](https://github.com/EnumC/me405/blob/main/final/res/gunphoto.jpg?raw=true)

The Mciver Autonomous Nerf Blaster is a heat-seeking auto-aiming turret that finds and shoots foam darts at human beings. Humans are tracked by an infared camera, so realistically, the turret will fire at anything that is on average hotter than the surrounding environment. 

The Mciver Autonomous Nerf Blaster was used to provide hands-on experience for ME405 students. Students at the end of the quarter used their design to face off in a tournament against their classmates who have also built their own autonomous turret. 
Welcome to the McIver Autonomous Nerf Turret. The McIver Autonomous Nerf Blaster is an auto-aiming turret that detects and shoots foam darts at targets using a heat-seeking infrared camera. Equipped with an infrared camera, the turret can track and target any object that emits heat greater than the surrounding environment. This project was executed as a hands-on experience for ME405 students, who designed their own autonomous turrets to participate in a tournament at the end of the quarter.

#  Hardware

The project's objective is to create a system that can control the rotation of two mutually exclusive axes. The project controls the pan and tilt mechanisms to aim the Nerf Gun. To implement this, our pan axis uses Ametek-Pittman motor, while our tilt axis uses a hobby servo.

## Tilt

Tilt is the simpler of the two axes to actuate. When aiming the nerf turret, tilt is sensitive because even a slight downward tilt can cause the dart to hit the floor, while a slight upward tilt can cause the dart to fly over the target's head. However, it does not require heavy adjustments. A good centering protocol and secure fastening of the mount ensure accuracy in this axis.

Since only one axis needed to use the Pittman motors, we decided not to use them for this axis, benefiting the precision. Instead, this axis is controlled by a servo with a 3D-printed servo mount. The servo mount features a screw terminal that allows the mounting of an iPad arm with the same screw terminal. Therefore, the iPad mount is bolted directly onto the small servo mount.

![servo mount](https://github.com/EnumC/me405/blob/main/final/res/servo%20mount.jpg?raw=true)
Figure 1: 3-D printer Servo Mount. There is a nut and bolt to connect the iPad arm to the servo mount. The servo mount is screwed into the screw terminal of the servo motor

Then the gun was mounted on the Ipad arm where the springs clamped the object to the arm, the same mechanism that holds the iPad in place. The Nerf Gun was then hot-glued securely onto the iPad arm. 

![ipad arm](https://github.com/EnumC/me405/blob/main/final/res/ipadarm.jpg?raw=true)
Figure 2: The iPad Arm holding the gun in place.

## Pan

Pan is the more challenging axis to rotate. We designed a Lazy Susan that the Pittman motor actuates. Figure 3 shows the mechanical design underneath the lazy susan cutting board. The design features a 3D-printed gear, a piece of wood to elevate the platform, and a bearing to allow the lazy susan to rotate on top of the base plate.

<img src="https://github.com/EnumC/me405/blob/main/final/res/lazysusan1.jpg?raw=true" width="1000">

<img src="https://github.com/EnumC/me405/blob/main/final/res/lazy%20susan%202.jpg?raw=true" width="1000">

Figure 3: Picture of the bottom side of the cutting board
The bottom gear of the lazy susan is attached to a gear on the side that the Pittman motor actuates. We will refer to that gear as the "top gear".



Figure 4 shows the gearbox that allows a sideways rotating motor to actuate a vertically rotating gear that is parallel to the ground. The motor is clamped by a sheet of aluminum securely onto the wooden base plate.


<img src="https://github.com/EnumC/me405/blob/main/final/res/gearbox1.jpg?raw=true" width="1000">

Figure 4: The gearbox. "Top gear" is the gear above the gearbox. 

<img src="https://github.com/EnumC/me405/blob/main/final/res/gearbox2.jpg?raw=true" width="1000">
Figure 5: Picture of the gearbox close up.

We used hot glue in this gearbox. First, it provided enough normal force to attach the teeth of the motor to the gears. Second, the "top gear" must be coupled with the shaft, but also be separately 3D printed. Superglue failed to dry overnight, and 2-part epoxy glued the top gear onto the non-rotating plate. Our solution was to insert a screw into a plastic terminal and use the surface area of the plastic to hot glue it against the walls of the hollow gear shaft. The screw head is also hot-glued onto the "top gear".

## Electronics Box, Wiring of the Firing Mechanism

![electronicsbox1](https://github.com/EnumC/me405/blob/main/final/res/electronicsbox1.jpg?raw=true)
Figure 6: Real life Wiring display

The Nerf gun that we chose had a peculiar firing mechanism. It had a proprietary onboard firing control unit (fcu). There are three main components to this black box -- the the power supply enable switch, the flywheel enable switch, and the loader enable switch. These consisted of two wires connected via a mechanical relay. 

![wiringdiagram](https://github.com/EnumC/me405/blob/main/final/res/wiringdiagram.jpg?raw=true)
Figure 7: Wiring Diagram of the firing mechanism

When the mechanical relay was engaged, the two wires would short and tell the firing control unit to power the respective device. For our purposes, we found that removing the switches and permanently connecting the wires together corresponding to the power supply enable and the fly wheel would allows us to signal the loading mechanism to fire individually. Via experimentation, the most reliable way to signal the loading mechanism was to send 3.3 volts from the microcontroller to the enable wire on the firing control unit. Therefore, simply turning this on and off would allow the gun to load bullets as we needed. The gun came with integrated firing modes determined by a physical switch. By setting it to single fire, we guaranteed that only one bullet would fire per signal sent regardless of how long the signal was sent. 

# Software

The software documentation can be found at [https://enumc.github.io/me405/final/docs/html/](https://enumc.github.io/me405/final/docs/html/).

The MotorDriver, EncoderReader, and Controller classes create a proportional controller for our motor. This controller is encapsulated in the FakeServo class, which allows for interaction with the electric motor in terms of angles (i.e. rotating 180 degrees). Our main competition code can be found in `main.py` and `camtest.py`. camtest.py instantiates all neccessary classes, determine firing kinematics, and control firing control.

## Motor Control

The pan cannot simply take inputs of angles because it uses an encoder motor. We found that the encoder value of 180 degrees rotation of the pan maps to an integer value of "69000". Therefore, it was necessary to input an angle divided by a ratio of some constants * 69000. The mathematics of this division is implemented in the "FakeServo driver". This abstracts the integral control of the motor, and allows it to behave much like a servo. It is much easier to control two servo-like objects when given a 2-D array (picture from the IR camera) than it is to deal with an encoder-based system and a servo-based system at the same time.

We also wrote a Servo driver to interact with the servo motor that controls the tilt of our turret. As the servo rotated, the gun would tilt exactly that number of degrees. Figure 3 shows that the servo's head is the axis of rotation. Controlling tilt was merely a change in degrees of the servo arm.

## Camera Control

The MLX_cam class was written to interact with the camera. Our turret takes in an image from the camera and applies a high pass filter over it, replacing the image with a binary version. In the binary map, 1's represent heat, and 0's represent darkness. We then search for clusters of heat over this binary map and locate a point in the picture to call our "average". This point data is used to control the rotation of the gun. A repetition of 3 points in the same location, meaning the picture has not changed and the target is still, would trigger the gun to fire. If this target moves, then another repeat of 3 pictures producing the same point would be needed to fire the gun again.

![camera](https://github.com/EnumC/me405/blob/main/final/res/camera1.jpg?raw=true)
Figure 8: The IR camera mount.

# Testing

How did you test your system?  How well has your system performed in these tests?

We need to translate a flat 2-D picture given by the camera into units of degrees of rotation to use as inputs into our mechanical system. However, we realized that we can use angles from the camera itself. The datasheet specifies that the camera has a field of view of 35 degrees up and down and 55 degrees left and right. Therefore, the location of the where to fire based on the 2-D array becomes dividing the total number of pixels with the respective degree on the axis. For example, if the point is located at the right most and top most pixel, the gun would rotate right by 55/2 degrees and up by 35/2 degrees.

We tested our setup via code review and experimental confirmations. We first validated our motor and servo controls. Then, we experimentally confirmed our IR hotspot detection by capturing IR data as a 2D array. Finally, we tested our system integration by testing our design in lab. 

# Discussions and Lessons

With a group of 2 CPE's and 1 GENE, this project challenged our mechanical design skills and allowed us to improve.
 
For the mechanics, we spent countless hours of trial and error in assembly. If something did not fit, we would add another layer of wood, cut a part, and add hot glue. This resulted in a difficult assembly process. With that being said, using off-the-shelf parts assisted with our prototype, given the increased ease of use for assembly.

In spite of our mechanical challenges, our code proved to be effective. Our turret performed beyond expectation for our lab on Thursday at 8AM. A functioning system requires both efficient code and well-designed hardware. In a future iteration, our turret will perform better and more reliably if given additional considerations in the mechanical assembly.

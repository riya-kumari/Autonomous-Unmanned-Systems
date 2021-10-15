# Contoller.py
# Blender:2.83, Python:3.7.x, OpenCV: >=3.3.x

import bpy
import sys

# Add Python 3.7 Environment Variables (Defined for LinImathux)
sys.path.append('/usr/local/bin/python3.9')
sys.path.append('/usr/local/include')
#sys.path.append('/usr/local/Cellar/')
sys.path.append('/usr/local/lib')
sys.path.append('/usr/local/bin')
sys.path.append('/usr/local/lib/python3.9/site-packages')

import math
import os
import random
import Imath
import array
import numpy as np
import cv2
#import OpenEXR
import math as Math

#file = OpenEXR.InputFile("/Users/riyakumari/Downloads/ASN3/Outputs/Depth/Depth0001.exr")


def SetRenderSettings():
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.eevee.taa_render_samples = 54 # Lowering this makes rendering fast but noisy
    bpy.context.scene.render.resolution_x = 320 # Reduce to speed up
    bpy.context.scene.render.resolution_y = 240 # Reduce to speed up

def Exr2Depth(exrfile):
    file = OpenEXR.InputFile(exrfile)

    # Compute the size
    dw = file.header()['dataWindow']
    ImgSize = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
    [Width, Height] = ImgSize

    # R and G channel stores the flow in (u,v) (Read Blender Notes)
    FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
    # start = timeit.default_timer()
    (R,G,B) = [array.array('f', file.channel(Chan, FLOAT)).tolist() for Chan in ("R", "G", "B")]
    # stop = timeit.default_timer()
    # print('Time: ', stop - start) 
    
    D = np.array(R).reshape(Height, Width, -1)
    D = (D <= 20. ) * D
 
    return D

    
def Render():    
    # DO NOT CHANGE THIS FUNCTION BELOW THIS LINE!        
    path_dir = bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path

    # Render Second Camera for Third Person view of the Drone
    cam = bpy.data.objects['Camera2']    
    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = os.path.join(path_dir, 'ThirdView', 'Frame%04d'%(bpy.data.scenes[0].frame_current))
    bpy.ops.render.render(write_still=True)

    # Render Drone Camera
    cam = bpy.data.objects['Camera']    
    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = os.path.join(path_dir, 'Frames', 'Frame%04d'%(bpy.data.scenes[0].frame_current))
    bpy.ops.render.render(write_still=True)
    
def VisionAndPlanner(GoalLocation, Camera):
    print(GoalLocation)
    # USE cv2.imread to the latest frame from 'Frames' Folder
    # HINT: You can get the latest frame using: bpy.data.scenes[0].frame_current
    # USE ReadEXR() function provided below to the latest depth image saved from 'Depth' Folder
    # Compute Commands to go left and right (VelX) using any method you like
    path_dir = bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path
    print(os.path.join(path_dir, 'Frames', 'Frame%04d'%(bpy.data.scenes[0].frame_current)))
    I = cv2.imread(os.path.join(path_dir, 'Frames', 'Frame%04d.png'%(bpy.data.scenes[0].frame_current)))
#    D = Exr2Depth(os.path.join(path_dir, 'Depth', 'Depth%04d.exr'%(bpy.data.scenes[0].frame_current)))
##    
    D = cv2.imread(os.path.join(path_dir, 'Depth', 'Depth%04d.exr'%(bpy.data.scenes[0].frame_current)),  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
#    print(D)
    # Converting depth exr to numpy array for further processing
#    channelData = dict()
#    for c in header['channels']:
#        C = exrfile.channel(c, Imath.PixelType(Imath.PixelType.FLOAT))
#        C = np.fromstring(C, dtype=np.float32)
#        C = np.reshape(C, isize)
#        
#        channelData[c] = C
#        print(channelData[c])
#    # You can visualize depth and image as follows
#    numpy.set_printoptions(threshold=sys.maxsize)
#    np.arange(100).reshape(25,4).tolist

    D = (D <= 20. ) * D
    D = np.array(D.tolist())
    print(D.length)
#    print(D.to.length)
#    cv2.imshow('Depth', D)
#    cv2.imshow('Image', I)
    cv2.waitKey(0)
    xDistance = GoalLocation[0] - Camera.location[0]
    yDistance = GoalLocation[1] - Camera.location[1]
    angle_theta = -1*math.atan2(yDistance, xDistance)
    newX = (Math.cos(angle_theta)*0.05)
    
    VelX = math.copysign(0.5, 0.5-random.uniform(0, 1))
    return newX

def Controller(TrafficCylinder, Camera):
    GoalReached = False # We are far from the goal when we start
    MaxFrames = 100 # Run it for a maximum of 100 frames
    OutOfBounds = False

    GoalLocation = [TrafficCylinder.location[0], TrafficCylinder.location[1], TrafficCylinder.location[2]]
    
        
    while(not (GoalReached or OutOfBounds or bpy.data.scenes['Scene'].frame_current>=MaxFrames)): 
        Render()   
        VelX = VisionAndPlanner(GoalLocation, Camera)      
        
        # World Axis Convention: +Y is front, +Z is up and +X is right
        # Change Location of the active object (in our case the Camera or our Drone)
        Camera.location[0] += VelX # Your controller changes this with feedback from vision
        Camera.location[1] += 1. # Forward velocity if fixed, m/frame, DO NOT CHANGE!
        # Camera.location[2] += VelZ # Perfect altittude hold, this does not change
        
        # Increment Frame counter so you know it's the next step
        bpy.data.scenes['Scene'].frame_set(bpy.data.scenes['Scene'].frame_current + 1)
        
        print(bpy.context.object.location)
        
        # DO NOT MODIFY BELOW THIS!
        DistToGoal = math.sqrt((GoalLocation[0]-Camera.location[0])**2 + (GoalLocation[1]-Camera.location[1])**2 + (GoalLocation[2]-Camera.location[2])**2)
        if(DistToGoal <= 2.):
            GoalReached = True
            print("Goal reached")
        if(Camera.location[0]<=-7.43413 or Camera.location[0]>=14.1931 or Camera.location[1]<=-50. or Camera.location[1]>=34.4089 or Camera.location[2]<=0. or Camera.location[2]>=10.):
            OutOfBounds = True
            print("out of bounds")
            

def main():
    SetRenderSettings()
    # Reset Frame to 0
    bpy.data.scenes['Scene'].frame_set(0)
    # Deselect all objects
    for obj in bpy.data.objects:
        obj.select_set(False)

    # Get Variables for objects we want to read/modify
    TrafficCylinder = bpy.data.objects['Traffic Cylinder']
    Camera = bpy.data.objects['Camera'] # This is the drone

    # Set camera to start point (DO NOT CHANGE THE START POINT OF THE CAMERA!)
    Camera.location[0] = 5.
    Camera.location[1] = -35.
    Camera.location[2] = 5.
    
    Controller(TrafficCylinder, Camera)


if __name__=="__main__":
    main()
    
    
    
     
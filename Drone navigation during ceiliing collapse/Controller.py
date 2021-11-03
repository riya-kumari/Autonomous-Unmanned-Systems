import bpy
import sys

sys.path.append('/usr/local/bin/python3.9')
sys.path.append('/usr/local/include')
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
import math as Math


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
#    cam = bpy.data.objects['Camera2']    
#    bpy.context.scene.camera = cam
#    bpy.context.scene.render.filepath = os.path.join(path_dir, 'ThirdView', 'Frame%04d'%(bpy.data.scenes[0].frame_current))
#    bpy.ops.render.render(write_still=True)

    # Render Drone Camera
    cam = bpy.data.objects['Camera']    
    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = os.path.join(path_dir, 'Frames', 'Frame%04d'%(bpy.data.scenes[0].frame_current))
    bpy.ops.render.render(write_still=True)
    
     # Render Drone
#    drone = bpy.data.objects['drone']    
#    bpy.context.scene.drone = drone
#    bpy.context.scene.render.filepath = os.path.join(path_dir, 'Frames', 'Frame%04d'%(bpy.data.scenes[0].frame_current))
#    bpy.ops.render.render(write_still=True)
    
    
def VisionAndPlanner(GoalLocation, Camera, Drone):
    print(GoalLocation)
    path_dir = bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path
    print(os.path.join(path_dir, 'Frames', 'Frame%04d'%(bpy.data.scenes[0].frame_current)))
    I = cv2.imread(os.path.join(path_dir, 'Frames', 'Frame%04d.png'%(bpy.data.scenes[0].frame_current)))
    
    # The depth maps are already being generated for us. Over here we are reading the values in from the depth maps and storing them in a numpy.ndArray    
    D = cv2.imread(os.path.join(path_dir, 'Depth', 'Depth%04d.exr'%(bpy.data.scenes[0].frame_current)),  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    #height : 240
    #width: 320

    print("D", D)
    
    leftmost_val = D[120,80][0]
    middle_val = D[120,160][0]
    rightmost_val = D[120,240][0]
    
    xDistance = GoalLocation[0] - Camera.location[0]
    yDistance = GoalLocation[1] - Camera.location[1] - 5
    angle_theta = -1*math.atan2(yDistance, xDistance)/5
    angle_theta = math.degrees(angle_theta)

##   Making the assumption that bot moves in the y direction at a speed of 3.1 units per iteration
    movement_toward_goal = (math.tan(angle_theta)/3.1)
#    
    obstacle_index = 0.2
    walls = 0.7
#    
    if leftmost_val < obstacle_index : 
        return math.copysign(0.8, 1)
    elif rightmost_val < obstacle_index: 
        return math.copysign(0.8, -1)
    else : 
        return movement_toward_goal
    
#    return math.copysign(0.8, 1)
    

def Controller(Victim, Camera, Drone):
    GoalReached = False # We are far from the goal when we start
    MaxFrames = 100 # Run it for a maximum of 100 frames
    OutOfBounds = False
    
    GoalLocation = [Victim.location[0], Victim.location[1], Victim.location[2]]

    while(not (GoalReached or OutOfBounds or bpy.data.scenes['Scene'].frame_current>=MaxFrames)): 
        Render()   
        VelX = VisionAndPlanner(GoalLocation, Camera, Drone)  
        
        Camera.location[0] += VelX # Your controller changes this with feedback from vision
        Camera.location[1] += 1.
        
        bpy.data.scenes['Scene'].frame_set(bpy.data.scenes['Scene'].frame_current + 1)
        
#        print(bpy.context.object.location)
        
        DistToGoal = math.sqrt((GoalLocation[0]-Camera.location[0])**2 + (GoalLocation[1]-Camera.location[1])**2 + (GoalLocation[2]-Camera.location[2])**2)
        if(DistToGoal <= 5.):
            GoalReached = True
            print("Goal reached")
#        if(Camera.location[0]>=22. or Camera.location[0]>=12. or Camera.location[1]>=. or Camera.location[1]>=34.4089 or Camera.location[2]<=0. or Camera.location[2]>=0.17.):
#            OutOfBounds = True
#            print("out of bounds")


def main():
    SetRenderSettings()
    # Reset Frame to 0
    bpy.data.scenes['Scene'].frame_set(0)
    # Deselect all objects
    for obj in bpy.data.objects:
        obj.select_set(False)

    # Get Variables for objects we want to read/modify
    Victim = bpy.data.objects['Suzanne']
    Camera = bpy.data.objects['Camera']
    Drone = bpy.data.objects['Empty']

    # Set camera to start point (DO NOT CHANGE THE START POINT OF THE CAMERA!)
    Camera.location[0] = -40.
    Camera.location[1] = -22.
    Camera.location[2] = 4.
    
    Controller(Victim, Camera, Drone)


if __name__=="__main__":
    main()

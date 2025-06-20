from .pepper_connection import PepperConnection
import time

def execute_movement():
    """
    Execute the movement sequence for the 'happy' emotion.
    This creates a celebratory, upbeat movement sequence.
    """
    # Initialize connection to Pepper
    pepper = PepperConnection()
    
    try:
        # Start from a neutral position
        pepper.go_to_posture("Stand", 0.5)
        pepper.wait_for_movement()
        
        # 1. Raise arms in a celebratory gesture
        joint_names = ["RShoulderPitch", "LShoulderPitch", "RShoulderRoll", "LShoulderRoll"]
        angles = [-1.0, -1.0, -0.5, 0.5]  # Raise arms up and slightly out
        pepper.move_joints(joint_names, angles, 0.6)
        pepper.wait_for_movement()
        
        # 2. Slight bouncing movement
        for _ in range(2):
            # Bend knees slightly
            pepper.move_joint("RKneePitch", 0.3, 0.4)
            pepper.move_joint("LKneePitch", 0.3, 0.4)
            pepper.wait_for_movement()
            
            # Return to standing
            pepper.move_joint("RKneePitch", 0.0, 0.4)
            pepper.move_joint("LKneePitch", 0.0, 0.4)
            pepper.wait_for_movement()
        
        # 3. Gentle swaying from side to side
        for _ in range(2):
            # Sway right
            pepper.move_joint("HipRoll", -0.1, 0.3)
            pepper.wait_for_movement()
            
            # Sway left
            pepper.move_joint("HipRoll", 0.1, 0.3)
            pepper.wait_for_movement()
        
        # 4. Return to neutral position
        pepper.go_to_posture("Stand", 0.5)
        pepper.wait_for_movement()
        
    except Exception as e:
        print(f"Error during happy movement: {e}")
    finally:
        # Always disconnect properly
        pepper.disconnect()

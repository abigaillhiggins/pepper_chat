from .pepper_connection import PepperConnection
import time

def execute_movement():
    """
    Execute the movement sequence for the 'sad' emotion.
    This creates a subdued, melancholic movement sequence.
    """
    # Initialize connection to Pepper
    pepper = PepperConnection()
    
    try:
        # Start from a neutral position
        pepper.go_to_posture("Stand", 0.5)
        pepper.wait_for_movement()
        
        # 1. Lower head slightly
        pepper.move_joint("HeadPitch", 0.3, 0.3)  # Tilt head down
        pepper.wait_for_movement()
        
        # 2. Drooping shoulders
        joint_names = ["RShoulderPitch", "LShoulderPitch", "RShoulderRoll", "LShoulderRoll"]
        angles = [0.5, 0.5, -0.2, 0.2]  # Lower shoulders and bring arms in
        pepper.move_joints(joint_names, angles, 0.4)
        pepper.wait_for_movement()
        
        # 3. Slow, gentle movement
        # Slight forward lean
        pepper.move_joint("HipPitch", 0.2, 0.2)
        pepper.wait_for_movement()
        
        # Gentle sway
        for _ in range(2):
            pepper.move_joint("HipRoll", -0.05, 0.2)
            pepper.wait_for_movement()
            pepper.move_joint("HipRoll", 0.05, 0.2)
            pepper.wait_for_movement()
        
        # 4. Return to neutral position
        pepper.go_to_posture("Stand", 0.3)
        pepper.wait_for_movement()
        
    except Exception as e:
        print(f"Error during sad movement: {e}")
    finally:
        # Always disconnect properly
        pepper.disconnect()

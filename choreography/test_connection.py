from pepper_connection import PepperConnection
import time

def test_connection():
    """Test the connection to Pepper and basic movement functionality."""
    print("Testing connection to Pepper...")
    
    # Create connection
    pepper = PepperConnection()
    
    if not pepper.connected:
        print("Failed to connect to Pepper. Please check:")
        print("1. Pepper is powered on")
        print("2. Pepper is on the same network")
        print("3. IP address is correct (10.0.0.244)")
        print("4. REST API is enabled on Pepper")
        return
    
    print("\nConnection successful! Testing basic movements...")
    
    try:
        # Test 1: Go to stand posture
        print("\nTest 1: Going to stand posture...")
        pepper.go_to_posture("Stand", 0.5)
        pepper.wait_for_movement()
        print("✓ Stand posture test complete")
        
        # Test 2: Move head
        print("\nTest 2: Moving head...")
        pepper.move_joint("HeadPitch", 0.2, 0.3)  # Look down slightly
        pepper.wait_for_movement()
        pepper.move_joint("HeadPitch", 0.0, 0.3)  # Return to center
        pepper.wait_for_movement()
        print("✓ Head movement test complete")
        
        # Test 3: Move arms
        print("\nTest 3: Moving arms...")
        joint_names = ["RShoulderPitch", "LShoulderPitch"]
        angles = [-0.5, -0.5]  # Raise arms slightly
        pepper.move_joints(joint_names, angles, 0.3)
        pepper.wait_for_movement()
        angles = [0.0, 0.0]  # Return to neutral
        pepper.move_joints(joint_names, angles, 0.3)
        pepper.wait_for_movement()
        print("✓ Arm movement test complete")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
    finally:
        # Always disconnect properly
        print("\nDisconnecting from Pepper...")
        pepper.disconnect()
        print("Disconnected successfully")

if __name__ == "__main__":
    test_connection() 
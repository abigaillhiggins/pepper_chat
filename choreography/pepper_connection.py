import requests
import json
import time
from typing import Optional, Dict, List

class PepperConnection:
    """
    Handles connection to Pepper robot using REST API.
    This version doesn't require local NAOqi SDK installation.
    """
    def __init__(self, ip: str = "10.0.0.244", port: int = 5000):
        """
        Initialize connection to Pepper robot.
        
        Args:
            ip (str): Pepper's IP address (default is 10.0.0.244)
            port (int): Pepper's port (default is 5000)
        """
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}"
        self.connected = False
        self.connect()
    
    def connect(self) -> bool:
        """
        Establish connection to Pepper using REST API.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Test connection by getting robot state
            response = requests.get(f"{self.base_url}/robot/state")
            if response.status_code == 200:
                self.connected = True
                print("Successfully connected to Pepper")
                return True
            else:
                print(f"Failed to connect to Pepper: {response.status_code}")
                return False
        except Exception as e:
            print(f"Failed to connect to Pepper: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Pepper and put it in rest position."""
        if self.connected:
            try:
                # Send rest command
                requests.post(f"{self.base_url}/robot/rest")
                self.connected = False
            except Exception as e:
                print(f"Error during disconnect: {e}")
    
    def move_joint(self, joint_name: str, angle: float, speed: float = 0.5):
        """
        Move a specific joint to a target angle.
        
        Args:
            joint_name (str): Name of the joint to move
            angle (float): Target angle in radians
            speed (float): Movement speed (0.0 to 1.0)
        """
        if not self.connected:
            return
        
        try:
            data = {
                "joint": joint_name,
                "angle": angle,
                "speed": speed
            }
            response = requests.post(
                f"{self.base_url}/motion/joint",
                json=data
            )
            if response.status_code != 200:
                print(f"Failed to move joint: {response.status_code}")
        except Exception as e:
            print(f"Error moving joint: {e}")
    
    def move_joints(self, joint_names: List[str], angles: List[float], speed: float = 0.5):
        """
        Move multiple joints simultaneously.
        
        Args:
            joint_names (list): List of joint names
            angles (list): List of target angles
            speed (float): Movement speed (0.0 to 1.0)
        """
        if not self.connected or len(joint_names) != len(angles):
            return
        
        try:
            data = {
                "joints": joint_names,
                "angles": angles,
                "speed": speed
            }
            response = requests.post(
                f"{self.base_url}/motion/joints",
                json=data
            )
            if response.status_code != 200:
                print(f"Failed to move joints: {response.status_code}")
        except Exception as e:
            print(f"Error moving joints: {e}")
    
    def go_to_posture(self, posture_name: str, speed: float = 0.5):
        """
        Move to a predefined posture.
        
        Args:
            posture_name (str): Name of the posture
            speed (float): Movement speed (0.0 to 1.0)
        """
        if not self.connected:
            return
        
        try:
            data = {
                "posture": posture_name,
                "speed": speed
            }
            response = requests.post(
                f"{self.base_url}/motion/posture",
                json=data
            )
            if response.status_code != 200:
                print(f"Failed to go to posture: {response.status_code}")
        except Exception as e:
            print(f"Error going to posture: {e}")
    
    def wait_for_movement(self, timeout: float = 2.0):
        """
        Wait for current movement to complete.
        
        Args:
            timeout (float): Maximum time to wait in seconds
        """
        if not self.connected:
            return
        
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            try:
                response = requests.get(f"{self.base_url}/motion/status")
                if response.status_code == 200:
                    status = response.json()
                    if not status.get("is_moving", False):
                        break
            except Exception as e:
                print(f"Error checking movement status: {e}")
                break
            time.sleep(0.1) 
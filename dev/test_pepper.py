from agents.pepper_agent import PepperAgent

def main():
    print("Testing Pepper's new personality...")
    print("Type 'quit' to exit.")
    print("\nPepper is ready to chat!")
    
    pepper = PepperAgent()
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
            
        response = pepper.get_response(user_input)
        print(f"\nPepper: {response}")

if __name__ == "__main__":
    main() 
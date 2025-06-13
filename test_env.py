from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("ELEVENLABS_API_KEY:", os.getenv("ELEVENLABS_API_KEY"))

def test_env_vars():
    # Load environment variables
    load_dotenv()
    
    # Get the environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    playht_key = os.getenv('PLAYHT_API_KEY')
    playht_user = os.getenv('PLAYHT_USER_ID')
    
    # Print the values (partially masked for security)
    print("\nEnvironment Variables Check:")
    print("-" * 30)
    
    if openai_key:
        masked_key = openai_key[:8] + "..." + openai_key[-4:] if len(openai_key) > 12 else "***"
        print(f"OPENAI_API_KEY: {masked_key}")
    else:
        print("OPENAI_API_KEY: Not found")
        
    if playht_key:
        masked_key = playht_key[:8] + "..." + playht_key[-4:] if len(playht_key) > 12 else "***"
        print(f"PLAYHT_API_KEY: {masked_key}")
    else:
        print("PLAYHT_API_KEY: Not found")
        
    if playht_user:
        masked_user = playht_user[:4] + "..." + playht_user[-4:] if len(playht_user) > 8 else "***"
        print(f"PLAYHT_USER_ID: {masked_user}")
    else:
        print("PLAYHT_USER_ID: Not found")
    
    # Check if all required variables are present
    missing_vars = []
    if not openai_key:
        missing_vars.append('OPENAI_API_KEY')
    if not playht_key:
        missing_vars.append('PLAYHT_API_KEY')
    if not playht_user:
        missing_vars.append('PLAYHT_USER_ID')
    
    if missing_vars:
        print("\nMissing environment variables:")
        for var in missing_vars:
            print(f"- {var}")
    else:
        print("\nAll required environment variables are present!")

if __name__ == "__main__":
    test_env_vars() 
import pyautogui
import time
import json
import os
import pyperclip

# Configuration file to store Claude Desktop position
CONFIG_FILE = "config/claude_desktop_config.json"

def save_claude_position():
    """
    Save Claude Desktop position to config file
    """
    print("Please click on Claude Desktop's chat input area to save its position...")
    print("You have 5 seconds to click...")
    
    # Countdown
    for i in range(5, 0, -1):
        print(i)
        time.sleep(1)
    
    # Get current mouse position
    x, y = pyautogui.position()
    
    # Create config directory if it doesn't exist
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    
    # Save to config file
    config = {"x": x, "y": y}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    
    print(f"Claude Desktop position saved: ({x}, {y})")
    return x, y

def load_claude_position():
    """
    Load Claude Desktop position from config file
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config["x"], config["y"]
    return None

def send_to_claude_desktop(message, x=None, y=None):
    """
    Send message to Claude Desktop chat input
    
    Args:
        message (str): Message to send
        x (int): X coordinate of chat input (optional)
        y (int): Y coordinate of chat input (optional)
    """
    # If coordinates provided, click there first
    if x is not None and y is not None:
        pyautogui.click(x, y)
        time.sleep(0.5)
    else:
        # Wait a bit for Claude Desktop to be active
        time.sleep(2)
    
    # Use clipboard for Japanese text to avoid IME issues
    pyperclip.copy(message)
    time.sleep(0.5)  # Wait for clipboard to be set
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.8)  # Wait for paste to complete
    
    # Press Enter to send
    pyautogui.press('enter')

if __name__ == "__main__":
    # Always save Claude Desktop position (overwrites existing)
    print("Saving Claude Desktop position...")
    x, y = save_claude_position()
    print("Setup complete!")

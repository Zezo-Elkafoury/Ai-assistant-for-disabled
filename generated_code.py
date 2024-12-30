import subprocess
import sys

def open_youtube_app():
    """Opens the YouTube application."""

    try:
        if sys.platform.startswith('win'):
            subprocess.Popen(['start', 'youtube:'], shell=True)  # Windows
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open', 'youtube://'])  # macOS
        elif sys.platform.startswith('linux'):
            subprocess.Popen(['xdg-open', 'youtube://'])  # Linux
        else:
            print("Unsupported operating system.")
    except FileNotFoundError:
        print("Error: YouTube application not found or xdg-open command not available.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_youtube_app()
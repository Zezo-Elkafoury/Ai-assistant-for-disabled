import customtkinter as ctk
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import threading
import os
from time import sleep
from dotenv import load_dotenv

load_dotenv()

class VoiceChatBot:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AI Voice Assistant")
        
        # Window positioning
        width = 400
        height = 600
        x = self.root.winfo_screenwidth() - width - 20
        self.root.geometry(f"{width}x{height}+{x}+20")
        
        self.root.attributes("-topmost", True)
        ctk.set_appearance_mode("dark")
        
        # Initialize voice components
        self.recognizer = sr.Recognizer()
        self.setup_tts_engine()
        self.is_listening = False
        
        # Initialize Gemini
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-002",
            system_instruction="""You are a prompt engineer. Help users clarify their requests with follow-up questions. Once refined, write: FINAL PROMPT: followed by the user's refined prompt."""
        )
        self.chat = self.model.start_chat(history=[])
        
        self.setup_ui()
        
    def setup_tts_engine(self):
        """Initialize text-to-speech engine with error handling"""
        try:
            self.engine = pyttsx3.init()
            # Set properties for better speech
            self.engine.setProperty('rate', 150)  # Slower rate for clarity
            voices = self.engine.getProperty('voices')
            # Try to set a female voice if available
            for voice in voices:
                if "female" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"TTS Engine initialization error: {str(e)}")
            self.engine = None
    
    def setup_ui(self):
        # Colors
        bg_color = "#1E1E1E"
        input_bg = "#2D2D2D"
        accent_color = "#007AFF"
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color=bg_color)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            text_color="#666666",
            font=("Inter", 11)
        )
        self.status_label.pack(fill="x", pady=(0, 5))
        
        # Chat area
        self.messages_area = ctk.CTkTextbox(
            self.main_frame,
            wrap="word",
            font=("Inter", 12),
            fg_color=input_bg,
            text_color="white",
            corner_radius=10
        )
        self.messages_area.pack(fill="both", expand=True, pady=(0, 10))
        self.messages_area.configure(state="disabled")
        
        # Input container
        input_container = ctk.CTkFrame(self.main_frame, fg_color=bg_color)
        input_container.pack(fill="x", pady=(0, 5))
        
        # Input field
        self.input_field = ctk.CTkTextbox(
            input_container,
            height=40,
            wrap="word",
            font=("Inter", 12),
            fg_color=input_bg,
            text_color="white",
            corner_radius=10
        )
        self.input_field.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Microphone button
        self.mic_button = ctk.CTkButton(
            input_container,
            text="🎤",
            width=40,
            height=40,
            command=self.toggle_voice_input,
            fg_color=input_bg,
            hover_color="#3D3D3D",
            corner_radius=10,
            font=("Inter", 16)
        )
        self.mic_button.pack(side="right", padx=(0, 5))
        
        # Send button
        self.send_button = ctk.CTkButton(
            input_container,
            text="→",
            width=40,
            height=40,
            command=self.send_message,
            font=("Inter", 16, "bold"),
            fg_color=accent_color,
            hover_color="#0056b3",
            corner_radius=10
        )
        self.send_button.pack(side="right")
        
        # Key bindings
        self.root.bind('<Control-m>', lambda e: self.toggle_voice_input())
        self.input_field.bind("<Return>", lambda e: self.send_message() if not e.state & 0x1 else None)
        self.input_field.bind("<Shift-Return>", lambda e: None)
        
        # Welcome message
        self.add_bot_message("How can I help? (Press Ctrl+M for voice input)")
    
    def toggle_voice_input(self):
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()
    
    def start_listening(self):
        self.is_listening = True
        self.mic_button.configure(fg_color="#007AFF")
        self.status_label.configure(text="Listening... (Ctrl+M to stop)")
        threading.Thread(target=self.listen_for_speech, daemon=True).start()
    
    def stop_listening(self):
        self.is_listening = False
        self.mic_button.configure(fg_color="#2D2D2D")
        self.status_label.configure(text="")
    
    def listen_for_speech(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                self.root.after(0, self.process_voice_input, text)
            except sr.WaitTimeoutError:
                self.root.after(0, self.show_error, "No speech detected")
            except sr.UnknownValueError:
                self.root.after(0, self.show_error, "Could not understand audio")
            except Exception as e:
                self.root.after(0, self.show_error, f"Error: {str(e)}")
            finally:
                self.root.after(0, self.stop_listening)
    
    def process_voice_input(self, text):
        self.input_field.delete("1.0", "end")
        self.input_field.insert("1.0", text)
        self.send_message()
    
    def show_error(self, message):
        self.status_label.configure(text=message)
        self.root.after(3000, lambda: self.status_label.configure(text=""))
    
    def speak_text(self, text):
        """Speak text with error handling"""
        if not self.engine:
            print("Text-to-speech engine not available")
            return

        def speak():
            try:
                # Clean up the text for speech
                cleaned_text = text.replace('FINAL PROMPT:', '').strip()
                self.engine.say(cleaned_text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {str(e)}")

        threading.Thread(target=speak, daemon=True).start()
    
    def add_user_message(self, message):
        self.messages_area.configure(state="normal")
        self.messages_area.insert("end", "\n\nYou: ", "user_header")
        self.messages_area.insert("end", f"{message}\n", "user_message")
        self.messages_area.configure(state="disabled")
        self.messages_area.see("end")
    
    def add_bot_message(self, message):
        self.messages_area.configure(state="normal")
        self.messages_area.insert("end", "\n\nAI: ", "bot_header")
        self.messages_area.insert("end", f"{message}\n", "bot_message")
        self.messages_area.configure(state="disabled")
        self.messages_area.see("end")
        
        # Speak the response
        self.speak_text(message)
    
    def send_message(self):
        message = self.input_field.get("1.0", "end-1c").strip()
        if not message:
            return
        
        self.input_field.delete("1.0", "end")
        self.add_user_message(message)
        
        try:
            response = self.chat.send_message(message).text
            self.add_bot_message(response)
            if "FINAL PROMPT" in response:
                with open('prompt.txt', 'w+') as f:
                    f.write(response)
                sleep(2)
                os.system("python3 components/gen_code.py")
        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.add_bot_message(error_message)
            self.speak_text("Sorry, I encountered an error.")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    VoiceChatBot().run()
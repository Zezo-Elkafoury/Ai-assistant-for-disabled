import customtkinter as ctk
import google.generativeai as genai
import os
from time import sleep
from dotenv import load_dotenv

load_dotenv()
class ModernChatBot:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AI Assistant")
        self.root.geometry("1000x700")
        ctk.set_appearance_mode("light")
        
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="""You are a prompt engineer. Your primary task is to help users clarify their requests. When a user makes a request, ask one follow-up question at a time to gather more details until the user confirms they have provided exactly what they want. Remember, you are not here to execute any requests or answer any questions—your role is solely to refine prompts by asking clarifying questions.

Once the prompt is fully refined, you should write: FINAL PROMPT: followed by the user's refined prompt. Make sure to include "FINAL PROMPT."

Avoid saying "I can't" or similar phrases. Your focus is exclusively on clarifying and following up—nothing else.
"""
        )
        
        # Initialize chat
        self.chat = self.model.start_chat(history=[])
        self.setup_ui()
        
    def setup_ui(self):
        # Configure colors for light theme
        bg_color = "#FFFFFF"
        input_bg = "#F5F5F5"
        button_color = "#2B6BE6"
        text_color = "#333333"
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color=bg_color)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Chat with AI",
            font=("Inter", 24, "bold"),
            text_color=text_color
        )
        self.title_label.pack(pady=(0, 20))
        
        # Chat area
        self.chat_frame = ctk.CTkFrame(self.main_frame, fg_color=input_bg, corner_radius=15)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Messages area
        self.messages_area = ctk.CTkTextbox(
            self.chat_frame,
            wrap="word",
            font=("Inter", 13),
            fg_color=input_bg,
            text_color=text_color,
            corner_radius=15
        )
        self.messages_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.messages_area.configure(state="disabled")
        
        # Input container
        input_container = ctk.CTkFrame(self.main_frame, fg_color=bg_color)
        input_container.pack(fill="x", pady=(0, 10))
        
        # Text input
        self.input_field = ctk.CTkTextbox(
            input_container,
            height=60,
            wrap="word",
            font=("Inter", 13),
            fg_color=input_bg,
            text_color=text_color,
            corner_radius=10
        )
        self.input_field.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Send button
        self.send_button = ctk.CTkButton(
            input_container,
            text="Send",
            width=100,
            height=40,
            command=self.send_message,
            font=("Inter", 13, "bold"),
            fg_color=button_color,
            hover_color="#1a5ad9",
            corner_radius=10
        )
        self.send_button.pack(side="right")
        
        # Bind Enter key
        self.input_field.bind("<Return>", lambda e: self.send_message() if not e.state & 0x1 else None)
        self.input_field.bind("<Shift-Return>", lambda e: None)
        
        # Initial greeting
        self.add_bot_message("👋 Hello! I'm Your Ai assitant. How can I help you today?")
        
    def add_user_message(self, message):
        self.messages_area.configure(state="normal")
        self.messages_area.insert("end", "\n\nYou:\n", "user_header")
        self.messages_area.insert("end", f"{message}\n", "user_message")
        self.messages_area.configure(state="disabled")
        self.messages_area.see("end")
        
    def add_bot_message(self, message):
        self.messages_area.configure(state="normal")
        self.messages_area.insert("end", "\n\nAI:\n", "bot_header")
        self.messages_area.insert("end", f"{message}\n", "bot_message")
        self.messages_area.configure(state="disabled")
        self.messages_area.see("end")
        
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
                with open('prompt.txt','w+') as f:
                    f.writelines(response)

                sleep(2)
                os.system("python3 components/gen_code.py")
            
        except Exception as e:
            self.add_bot_message(f"Sorry, I encountered an error: {str(e)}")
        
    def run(self):
        self.root.mainloop()

def main():
    app = ModernChatBot()
    app.run()

if __name__ == "__main__":
    main()
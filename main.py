# main.py
from chatbot_manager import ChatbotManager

def handle_conversation():
    print("Welcome to the AI ChatBot. Type 'exit' to quit.")
    
    folder_path = input("Enter folder path to upload files: ")
    chatbot_manager = ChatbotManager(folder_path)

    # 🟡 Add this line to load and split documents
    chatbot_manager.load_and_split_documents()

    while True:
        user_input = input("YOU: ")
        if user_input.lower() == "exit":
            break
        
        bot_response = chatbot_manager.get_response(user_input)
        print("Bot Response:", bot_response)

if __name__ == "__main__":
    handle_conversation()

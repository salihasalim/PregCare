import nltk
import random
import string
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

from nltk.chat.util import Chat, reflections

# Define pairs of patterns and responses
pairs = [
    (r"hi|hello|hey", ["Hello!", "Hi there!", "Hey! How can I help?"]),
    (r"how are you", ["I'm just a bot, but I'm doing great!", "I'm fine! What about you?"]),
    (r"what is your name", ["I'm a simple chatbot!", "You can call me ChatBot!"]),
    (r"bye|goodbye", ["Goodbye!", "See you soon!"]),
    (r"(.*) weather (.*)", ["I can't check the weather, but you can visit weather.com!"]),
    (r"(.*)", ["I'm not sure about that. Can you ask me something else?", "Hmm... I don't know."])
]

# Create a chatbot instance
chatbot = Chat(pairs, reflections)

# Function to get chatbot response
def get_bot_response(user_input):
    return chatbot.respond(user_input)

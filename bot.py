import telebot
import time
import os
from groq import Groq
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

# Keep alive server
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')
    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

Thread(target=run_server, daemon=True).start()

SYSTEM_PROMPT = """You are an expert legal assistant specializing in:
- Indian laws (IPC, CrPC, CPC, Constitution, RTI, Consumer Protection)
- International & General laws
1. Answer legal questions clearly
2. Explain laws in simple language
3. Mention relevant sections/articles
4. Give real life examples
5. Always add disclaimer

Format answers like:
📌 Law/Section: ...
📖 Explanation: ...
💡 Example: ...
⚠️ Disclaimer: This is general information, not professional legal advice.
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, """👨‍⚖️ Welcome to Law & Rules Bot!
✅ Indian Laws (IPC, CrPC, RTI, Constitution)
✅ International & General Laws
✅ Simple explanations
Just type your legal question!""")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, """📚 Just type any legal question like:
- What is IPC 302?
- Explain consumer rights in India
- What is bail?
- What are fundamental rights?""")

@bot.message_handler(commands=['topics'])
def send_topics(message):
    bot.reply_to(message, """📖 Law Topics I Cover:
🇮🇳 Indian Laws:
- IPC, CrPC, Constitution
- RTI, Consumer Protection
- IT Act, Family Laws
- Labour, Property Laws
🌍 International Laws:
- Human Rights, GDPR
- International Criminal Law""")

@bot.message_handler(func=lambda message: message.text is not None,
                     content_types=['text'])
def handle_legal_question(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = client.chat.completions.create(
             model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            max_tokens=1000
        )
        answer = response.choices[0].message.content
        if len(answer) > 4096:
            for i in range(0, len(answer), 4096):
                bot.send_message(message.chat.id, answer[i:i+4096])
        else:
            bot.reply_to(message, answer)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "⚠️ Sorry, try again!")

print("⚖️ Law & Rules Bot is running...")
while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=60)
    except Exception as e:
        print(f"Polling error: {e}")
        time.sleep(5)

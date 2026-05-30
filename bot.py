import telebot
import time
import os
from groq import Groq

# Read from environment variables (safe & secure)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

SYSTEM_PROMPT = """You are an expert legal assistant specializing in:
- Indian laws (IPC, CrPC, CPC, Constitution, RTI, Consumer Protection, etc.)
- International & General laws

Your job:
1. Answer legal questions clearly and accurately
2. Explain laws in simple easy language
3. Mention relevant sections/articles (e.g., IPC Section 302, Article 21)
4. Give real-life examples when helpful
5. Always add disclaimer that this is for information only

Format answers like:
📌 Law/Section: ...
📖 Explanation: ...
💡 Example: ...
⚠️ Disclaimer: This is general information, not professional legal advice.
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome = """👨‍⚖️ Welcome to Law & Rules Bot!

I can help you with:
✅ Indian Laws (IPC, CrPC, RTI, Constitution...)
✅ International & General Laws
✅ Simple explanations of complex legal terms
✅ Legal Q&A on any topic

Just type your legal question!

📌 Examples:
- What is IPC Section 420?
- What are my rights if arrested?
- What is RTI and how to use it?
- What is Article 21 of Constitution?
"""
    bot.reply_to(message, welcome)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """📚 How to use this bot:

Just type any legal question like:
- What is IPC 302?
- Explain consumer rights in India
- What is bail and how to get it?
- What are fundamental rights?
- Explain GDPR

/start - Welcome message
/help - This help message
/topics - See all law topics
"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['topics'])
def send_topics(message):
    topics = """📖 Law Topics I Cover:

🇮🇳 Indian Laws:
- IPC (Indian Penal Code)
- CrPC (Criminal Procedure Code)
- Constitution of India
- RTI (Right to Information)
- Consumer Protection Act
- IT Act / Cyber Laws
- Family & Marriage Laws
- Labour & Employment Laws
- Property Laws
- POCSO Act
- Motor Vehicle Act

🌍 International Laws:
- Human Rights Laws
- GDPR (Data Protection)
- International Criminal Law
- Business & Contract Laws

Just ask me anything! 👨‍⚖️
"""
    bot.reply_to(message, topics)

@bot.message_handler(func=lambda message: True)
def handle_legal_question(message):
    user_question = message.text
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_question}
            ],
            max_tokens=1000
        )
        answer = response.choices[0].message.content

        if len(answer) > 4096:
            for i in range(0, len(answer), 4096):
                bot.send_message(chat_id, answer[i:i+4096])
        else:
            bot.reply_to(message, answer)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "⚠️ Sorry, could not process your question. Please try again!")

print("⚖️ Law & Rules Bot is running...")

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=60)
    except Exception as e:
        print(f"Polling error: {e}")
        time.sleep(5)
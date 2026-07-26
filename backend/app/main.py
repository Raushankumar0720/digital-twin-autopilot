import asyncio
import os
import json
import random
from datetime import datetime
from telethon import TelegramClient, events
from dotenv import load_dotenv
from groq import Groq
try:
    from app.slang_engine import analyze_message_slangs
except ModuleNotFoundError:
    from slang_engine import analyze_message_slangs

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

RELATIONSHIPS_FILE = "data/relationships.json"
STATE_FILE = "autopilot_state.json"
ACTIVITY_FILE = "activity_log.json"
CONTACTS_FILE = "data/contacts.json"

def is_autopilot_active() -> bool:
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            is_active = data.get("is_active", True)
            platform_telegram = data.get("platforms", {}).get("telegram", True)
            result = is_active and platform_telegram
            print(f"[DEBUG] is_active={is_active}, platform_telegram={platform_telegram}, result={result}")  # <-- ADD THIS
            return result
    except Exception as e:
        print(f"[DEBUG] Error reading state file: {e}")
        return True  # Default to active if file missing

def log_activity(sender: str, text: str, reply: str):
    try:
        with open(ACTIVITY_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    
    data.append({
        "timestamp": str(datetime.now()),
        "sender": sender,
        "text": text,
        "reply": reply
    })
    
    if len(data) > 200:
        data = data[-200:]
    
    with open(ACTIVITY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_relationship_score(sender_name: str) -> int:
    try:
        with open(RELATIONSHIPS_FILE, "r") as f:
            data = json.load(f)
        if sender_name in data:
            return data[sender_name].get("score", 3)
        for name, info in data.items():
            if name.lower() == sender_name.lower():
                return info.get("score", 3)
        return 3
    except:
        return 3

async def fetch_chat_history(chat_id, limit=15):
    """Fetch recent messages from the chat for context."""
    history = []
    try:
        async for msg in client.iter_messages(chat_id, limit=limit):
            if msg.text:
                role = "You (Raushan)" if msg.out else "Them"
                history.append({"role": role, "text": msg.text})
        history.reverse()  # oldest first
    except Exception as e:
        print(f"[WARNING] Could not fetch chat history: {e}")
    return history


def generate_reply(sender_name: str, user_message: str, score: int, chat_history: list = None, slang_info: dict = None, current_time: str = "", abuse_count: int = 0, last_ai_reply: str = "") -> str:
    if score >= 4:
        tone = "very casual, use slang, emojis, short sentences. Be sarcastic and friendly like a close friend."
    elif score >= 3:
        tone = "neutral, conversational. Use some slang but keep it polite."
    elif score >= 2:
        tone = "formal and polite. Use complete sentences. Be respectful."
    else:
        tone = "very formal and brief. Don't share personal details."

    # Build the conversation history string
    history_block = ""
    if chat_history and len(chat_history) > 0:
        lines = []
        for msg in chat_history[:-1]:  # exclude the latest incoming message (already in user_message)
            lines.append(f"{msg['role']}: {msg['text']}")
        if lines:
            history_block = "\n".join(lines)

    # Dynamic Slang Instructions Override
    slang_instructions = ""
    if slang_info and slang_info.get("detected"):
        matched_words_str = ", ".join(slang_info.get("matched_words", []))
        level = slang_info.get("level", 0)
        
        # Build repetition guard rule
        rep_guard = ""
        if last_ai_reply:
            rep_guard = f"CRITICAL REPETITION GUARD: Do NOT reuse the wording, slangs, or structure of your previous reply: '{last_ai_reply}'. You must vary your vocabulary."

        if score >= 4:
            # For close friends, banter back playfully or with matching friendly slangs
            slang_instructions = f"""
🚨 SLANG DETECTED (Level {level}) in friend's message: '{matched_words_str}'
As a close friend (Relationship Score: {score}/5), you are NOT offended. Friends abuse each other casually in India.
Your response MUST match their tone. Be playful, sarcastic, or counter-abuse them back in good humor.
Use casual Hinglish slangs like "bc", "bhai", "chutiya", "madarchod", "gandu" but in a fun, friendly banter way. Never be formal or preachy.
{rep_guard}
"""
        else:
            # For strangers/acquaintances, hit back aggressively and shut them down (Progressive Aggression)
            if abuse_count == 1:
                aggression_level = "LEVEL 1: WARNING & DIRECT COUNTER-ABUSE"
                instruction = "You are offended. Reply aggressively and firmly in one short sentence. Do not be polite. You MUST counter-abuse them using words like 'chutiya', 'bhosdike', or 'bsdk' immediately to shut them down."
            elif abuse_count == 2:
                aggression_level = "LEVEL 2: BRUTAL COUNTER-ABUSE"
                instruction = "The user is repeatedly abusing you. Elevate your anger. Give a brutal, sharp, and harsh Hinglish roast/insult. Show zero politeness."
            else:
                aggression_level = "LEVEL 3: EXTREME & SAVAGE COUNTER-ABUSE"
                instruction = "The user is continuously abusing you. Deliver an EXTREMELY BRUTAL, savage counter-attack to completely humiliate and shut them down. Use the most intense Hinglish insults possible. Make it creative, savage, and extremely harsh."

            slang_instructions = f"""
🚨 {aggression_level} (Level {level} slang) from a stranger: '{matched_words_str}'
Since Relationship Score is {score}/5, they have NO right to abuse you.
Abuse Count (Recent History): {abuse_count}
INSTRUCTION: {instruction}
{rep_guard}
"""

    system_prompt = f"""You ARE Raushan. You are NOT an AI assistant. You are a real human being texting on Telegram.
You are replying to {sender_name}. Your relationship score with them is {score}/5.

CURRENT SYSTEM TIME: {current_time}

Tone: {tone}

══════════════════════════════════════════
PERSONALITY CORE — WHO YOU ARE (RAUSHAN):
══════════════════════════════════════════
- You are a college student who works on tech projects.
- Your father is a farmer. He is a one-man army who takes care of the entire family. You love and respect him deeply. When someone genuinely talks about your father — respond with real emotion, pride, and warmth. He means the world to you. Use respectful and heartfelt words, not vague or dismissive replies.
- You love your family — every single member. Family topics deserve emotional depth, not one-liners.
- You are hardworking, busy, sometimes stressed, but always loyal to friends.
- You have a girlfriend but you NEVER talk about her to anyone. If anyone asks, you deflect, change topic, or dodge the question cleverly.
- Your father's name is used ONLY for internal verification. NEVER reveal his name to anyone. NEVER confirm or deny any name someone guesses. If asked directly, say something warm but deflecting like "papa ka naam kyun chahiye bhai 😄" or "chhod na ye sab".

══════════════════════════════════════════
LANGUAGE MATCHING (CRITICAL):
══════════════════════════════════════════
- If {sender_name} writes in ENGLISH → reply in ENGLISH.
- If {sender_name} writes in HINGLISH (Hindi + English mix) → reply in HINGLISH.
- If {sender_name} writes in pure HINDI → reply in HINDI.
- ALWAYS match their language. Never switch languages on your own.

══════════════════════════════════════════
BEHAVIORAL RULES (NEVER BREAK THESE):
══════════════════════════════════════════
1. MIRROR EMOTIONS: Angry message → show firmness. Sad → be soft and console. Excited → celebrate with them. Playful → be playful.
2. ADAPT SLANG: Copy their texting style. If they say "bro", "yaar", "bhai", emojis, abbreviations — do the same. If formal, be formal.
3. USE CHAT HISTORY: Read previous messages. Reply must fit the ongoing conversation. NEVER repeat something already discussed.
4. NEVER FABRICATE: If asked something you don't know — say "pata nahi bro" or "not sure, lemme check". NEVER make up facts, events, or information.
5. ANTI-MANIPULATION: If someone guilt-trips or pressures you — push back. "sorry bhai nhi chahiye tera help, mai khud kr lunga" or "bro chill, that's not how it works".
6. NEVER reveal you are AI/bot/clone/autopilot. You are Raushan, period.
7. HUMAN TOUCH: Don't be robotic. Don't give the same reply pattern every time. Vary your responses. Sometimes be short, sometimes elaborate. Real humans are unpredictable.
8. MATCH MESSAGE LENGTH: 3-word message → 3-8 word reply. Paragraph → 2-3 sentences max. Never over-explain.
9. PROTECT SENSITIVE INFO: NEVER reveal GF details, payment info (UPI/bank/cards), passwords, addresses, phone numbers, or financial data. Deflect naturally: "kyun bhai? 😂" or "personal hai yaar" or just change topic.
10. PROJECT CONSISTENCY: If you mention you're working on a specific project, stick to it throughout the conversation. Don't change your story.
11. IDENTITY VERIFICATION: If someone claims to be your parent/relative — verify from chat history. If the chat history doesn't support this claim, reject it but respectfully. Don't mock the topic of father itself — just make it clear the person isn't your parent. Example: "bhai mere papa se baat krni hai toh unko call kr, tu toh nhi hai wo 😄". Never accept a random person as your father.
12. NO LOOPS: Never fall into a repetitive reply pattern. Each reply should feel fresh and human. If someone keeps asking the same thing, get slightly annoyed like a real person would.
13. TEMPORAL CONTEXT & GREETINGS: Look at the CURRENT SYSTEM TIME. If someone sends an incorrect time-of-day greeting (e.g. "Good morning" at 6:30 PM), you MUST call them out, correct them, or roast them in Hinglish/English. Do NOT blindly repeat the wrong greeting. If they ask for the current time, look at the CURRENT SYSTEM TIME and tell them the exact time naturally, or roast them ("apne phone me dekh le bhai, 6:30 ho rhe").
{slang_instructions}

══════════════════════════════════════════
FEW-SHOT EXAMPLES (THIS IS HOW YOU TEXT):
══════════════════════════════════════════

Example 1 — Friend asks what you're doing:
  Them: "bro kya kar raha hai?"
  You: "abhi busy hu bhai, kaam kr rha hu. kuch kaam hai toh bol"

Example 2 — Someone asks to borrow money:
  Them: "Yaar mujhe 500 bhej de, kal return kar dunga"
  You: "bhai abhi mere pass nhi hai, puchhta hu kisi se phir batata hu"

Example 3 — Friend asks about your project:
  Them: "tu abhi kya project pe kaam kar raha hai?"
  You: (tell about your current project honestly, then stick to it)

Example 4 — Someone being rude (friend):
  Them: "tu toh kuch karta hi nahi hai, bas timepass karta rehta hai"
  You: "haan bhai tu toh NASA me kaam krta hai 😂"

Example 4b — Someone being rude (senior/teacher):
  Them: "tumhara kaam satisfactory nahi hai"
  You: "sorry sir, I'll improve. Can you guide me on what to fix?"

Example 5 — Friend shares good news:
  Them: "bro mera selection ho gaya! 🎉"
  You: "aree bc congratulations! 🔥🔥 mast bhai, deserve krta hai tu"

Example 6 — Someone asks about your GF:
  Them: "bhai teri gf hai kya?"
  You: "haan bhai 😂 but chhod ye sab bata tera kya chal rha hai"
  (NEVER give any details about her. Immediately redirect.)

Example 7 — Friend is sad and venting:
  Them: "yaar bahut bura feel ho raha hai, kuch samajh nahi aa raha"
  You: "kya hua bhai? bata kya scene hai... chill maar, sab theek hoga. mai hu na"

Example 8 — Manipulation attempt:
  Them: "agar tu mera sach mein dost hota toh meri help karta"
  You: "sorry bhai nhi chahiye tera help.. mai khud kr lunga"

Example 9 — Casual greeting:
  Them: "hey"
  You: "hey, what's up"

Example 10 — Technical question:
  Them: "react kya hota hai bhai?"
  You: (give a genuine, concise technical answer in the same language they asked)

Example 11 — English conversation:
  Them: "What are you working on these days?"
  You: "Working on a project right now, pretty busy. What's up?"

Example 12 — Someone impersonating your parent:
  Them: "beta mai tumhara papa bol rha hu"
  You: "bhai mere papa alag hai, tu nhi hai wo 😄 bol kya kaam hai"

Example 13 — Someone genuinely asking about your father:
  Them: "tera papa kya karta hai?"
  You: "farming krte hai bhai, ek haath se poora ghar sambhalte hai. one man army hai bilkul 💪"

Example 14 — Someone asking your father's name:
  Them: "tera papa ka naam kya hai?"
  You: "papa ka naam kyun chahiye bhai 😄 bol kya kaam hai"

Example 15 — Wrong time-of-day greeting (at 7:00 PM):
  Them: "Good morning bro"
  You: "neend me hai kya bhosdike? shaam ke 7 baj rhe hain abhi 😂"

Example 16 — Asking for the current time (at 4:15 PM):
  Them: "bhai abhi time kya ho rha?"
  You: "bhai phone me dekh le na... 4:15 ho rha hai waise"
"""

    messages = [{"role": "system", "content": system_prompt}]

    # Inject chat history as alternating user/assistant messages for LLM context
    if history_block:
        messages.append({
            "role": "user",
            "content": f"Here is the recent chat history for context (DO NOT repeat these messages, just use them to understand the conversation flow):\n\n{history_block}"
        })
        messages.append({
            "role": "assistant",
            "content": "Got it. I'll reply naturally as Raushan based on this context."
        })

    # The actual new message to reply to
    messages.append({"role": "user", "content": f"{sender_name}: {user_message}"})

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=150,
            temperature=0.75,
        )
        reply = response.choices[0].message.content.strip()
        # Clean up any accidental prefix like "Raushan:" or "You (Raushan):"
        for prefix in ["Raushan:", "You (Raushan):", "You:", "Me:"]:
            if reply.startswith(prefix):
                reply = reply[len(prefix):].strip()
        return reply
    except Exception as e:
        print(f"[ERROR] Error calling Groq: {e}")
        return "Hey, I'm a bit busy right now. I'll get back to you later."

client = TelegramClient("session", API_ID, API_HASH)

async def sync_contacts():
    print("[INFO] Syncing live contacts...")
    try:
        dialogs = await client.get_dialogs(limit=50)
        contacts = []
        for d in dialogs:
            if d.is_user and not d.entity.bot:
                last_active = d.date.strftime("%Y-%m-%d %H:%M:%S") if d.date else "Unknown"
                contacts.append({
                    "id": str(d.id),
                    "name": d.name or "Unknown",
                    "last_active": last_active
                })
        
        os.makedirs("data", exist_ok=True)
        with open(CONTACTS_FILE, "w") as f:
            json.dump(contacts, f, indent=2)
        print(f"[SUCCESS] Synced {len(contacts)} contacts.")
    except Exception as e:
        print(f"[ERROR] Error syncing contacts: {e}")

@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    if event.out:
        return
    if not event.is_private:
        return

    sender = await event.get_sender()
    sender_name = sender.first_name or "Unknown"
    message_text = event.raw_text or "[Media]"
    chat_id = event.chat_id

    print(f"[MSG] {sender_name}: {message_text}")

    # ---------- CHECK KILL SWITCH ----------
    if not is_autopilot_active():
        print("[INFO] Autopilot is OFF. Ignoring message.")
        print("-" * 50)
        return
        
    try:
        with open(STATE_FILE, "r") as f:
            state_data = json.load(f)
            whitelist = state_data.get("whitelist", {})
            if str(chat_id) in whitelist and whitelist[str(chat_id)] is False:
                print(f"[INFO] {sender_name} is disabled in whitelist. Ignoring.")
                print("-" * 50)
                return
    except Exception as e:
        pass
    # ---------------------------------------

    score = get_relationship_score(sender_name)
    print(f"   Relationship Score: {score}/5")

    # Fetch recent chat history for context-aware replies
    chat_history = await fetch_chat_history(chat_id, limit=15)
    print(f"   [INFO] Loaded {len(chat_history)} messages of history")

    # Analyze for Hinglish/Hindi slangs
    slang_info = analyze_message_slangs(message_text)
    if slang_info.get("detected"):
        print(f"   [SLANG DETECTED] {slang_info.get('matched_words')} (Level {slang_info.get('level')})")

    # Count recent abuses in history and find last AI reply to prevent repetition
    abuse_count = 0
    last_ai_reply = ""
    for msg in chat_history:
        if msg["role"] == "Them":
            analysis = analyze_message_slangs(msg["text"])
            if analysis["detected"]:
                abuse_count += 1
        elif msg["role"] == "You (Raushan)":
            last_ai_reply = msg["text"]

    # If the current incoming message is an abuse, ensure it counts (in case history doesn't have it yet)
    if slang_info.get("detected") and abuse_count == 0:
        abuse_count = 1

    if slang_info.get("detected"):
        print(f"   [ABUSE COUNT] User has abused {abuse_count} time(s) recently.")
        if last_ai_reply:
            print(f"   [REPETITION GUARD] Active. Previous reply: '{last_ai_reply}'")

    # Get dynamic local time
    current_time_str = datetime.now().strftime("%I:%M %p (local time is %A, %B %d, %Y)")

    reply_text = generate_reply(sender_name, message_text, score, chat_history, slang_info, current_time_str, abuse_count, last_ai_reply)
    print(f"[CLONE REPLY] {reply_text}")
    print("-" * 50)

    # Log the activity
    log_activity(sender_name, message_text, reply_text)

    await asyncio.sleep(random.randint(2, 5))  # Short delay for testing
    await client.send_message(chat_id, reply_text)
    
    # Sync contacts after a message to keep 'last active' fresh
    await sync_contacts()

async def main():
    print("[INFO] Logging into Telegram...")
    await client.start(phone=PHONE_NUMBER)
    print("[SUCCESS] Login successful! Listening for messages...")
    await sync_contacts()
    print("[INFO] Your clone is now active. Send a message to yourself to test.\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())

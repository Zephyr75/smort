import ollama
import difflib
import re

MODEL = "llama3.2:1b-instruct-q4_K_M"
AVAILABLE_FILES = ["jazz_vibes.mp3", "rock_anthem.mp3", "lofi_beats.wav"]

# We use a very aggressive System Prompt here.
SYSTEM_PROMPT = """You are a robot OS. You ONLY speak in these 4 formats:
MUSIC("search_term")
WEATHER("city")
LIGHT("ON" or "OFF")
CHAT("response")

STRICT RULES:
- Never use the word 'COMMAND'.
- Never explain yourself.
- If you don't know what to do, use CHAT("...").

EXAMPLES:
User: "Tell a joke" -> CHAT("Why did the robot cross the road? To get to the charger!")
User: "Is it cold in London?" -> WEATHER("London")
User: "Play rock" -> MUSIC("rock")
User: "Lights out" -> LIGHT("OFF")"""

def process_voice_text(text):
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': f"User: {text} ->"} # The "->" encourages completion
            ],
            options={
                'temperature': 0,
                'stop': ["\n", "User:"] # Stop the model from rambling
            }
        )
        
        raw = response['message']['content'].strip()
        
        # --- THE RECOVERY PARSER ---
        # If the model says COMMAND("weather", "London"), we fix it to WEATHER("London")
        raw = raw.replace('COMMAND("weather", ', 'WEATHER(').replace('COMMAND("', 'CHAT("')

        # Standard Regex for valid COMMAND("ARG")
        match = re.search(r'([A-Z]+)\("(.*?)"\)', raw)
        
        if match:
            cmd, arg = match.group(1), match.group(2)
            if cmd == "MUSIC":
                closest = difflib.get_close_matches(arg, AVAILABLE_FILES, n=1, cutoff=0.1)
                return [f'MUSIC("{closest[0] if closest else "default.mp3"}")']
            return [f'{cmd}("{arg}")']
        
        return [f'CHAT("{raw[:40]}")']
            
    except Exception as e:
        return [f'ERROR("{str(e)[:20]}")']

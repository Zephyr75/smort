import ollama
import difflib
import re
from transformers import pipeline

# --- CONFIGURATION ---
# We use DistilBART for Zero-Shot: It's fast and doesn't need training for new labels.
INTENT_MODEL = "valhalla/distilbart-mnli-12-1"
# Standard NER for identifying locations and miscellaneous entities
NER_MODEL = "dbmdz/bert-large-cased-finetuned-conll03-english"
LLM_MODEL = "llama3.2:1b-instruct-q4_K_M"

AVAILABLE_MUSIC = ["jazz_vibes.mp3", "rock_anthem.mp3", "lofi_beats.wav"]
INTENT_LABELS = ["music", "weather", "light", "chat"]

print("Loading Neural Networks...")
classifier = pipeline("zero-shot-classification", model=INTENT_MODEL, device=-1) # device=-1 forces CPU
ner_tagger = pipeline("ner", model=NER_MODEL, aggregation_strategy="simple", device=-1)

def get_entities(text):
    """Uses NER to find Locations (LOC) or Miscellaneous (MISC) titles."""
    entities = ner_tagger(text)
    results = {"LOC": None, "MISC": None} # also supports PER(son) and ORG(anisation)
    for ent in entities:
        if ent['entity_group'] in results:
            results[ent['entity_group']] = ent['word']
    return results

def get_llm_chat(text):
    """Fallback to Llama for creative responses (jokes, greetings)."""
    response = ollama.chat(model=LLM_MODEL, messages=[
        {'role': 'system', 'content': 'You are a tiny robot. Keep answers under 15 words.'},
        {'role': 'user', 'content': text}
    ])
    return response['message']['content'].strip()

def process_request(text):
    print(f"\nProcessing: '{text}'")
    
    # 1. CLASSIFY INTENT
    intent_res = classifier(text, candidate_labels=INTENT_LABELS)
    intent = intent_res['labels'][0]
    confidence = intent_res['scores'][0]
    
    print(f"Intent: {intent} ({confidence:.2f})")

    # 2. DISPATCH LOGIC
    if confidence < 0.45:
        return f'CHAT("I am not sure what you mean.")'

    if intent == "music":
        # Try to find the song name using NER
        entities = get_entities(text)
        search_term = entities['MISC'] if entities['MISC'] else text
        # Fuzzy match against your actual MP3 files
        match = difflib.get_close_matches(search_term, AVAILABLE_MUSIC, n=1, cutoff=0.2)
        song = match[0] if match else "default.mp3"
        return f'MUSIC("{song}")'

    elif intent == "weather":
        entities = get_entities(text)
        city = entities['LOC'] if entities['LOC'] else "your location"
        return f'WEATHER("{city}")'

    elif intent == "light":
        state = "ON" if "on" in text.lower() else "OFF"
        return f'LIGHT("{state}")'

    else: # intent == "chat"
        response = get_llm_chat(text)
        return f'CHAT("{response}")'

# --- TEST SUITE ---
if __name__ == "__main__":
    tests = [
        "Play the rock anthem",
        "Is it raining in San Francisco?",
        "Turn the lights on please",
        "Tell me a short robot joke"
    ]
    for t in tests:
        print(f"PICO COMMAND: {process_request(t)}")

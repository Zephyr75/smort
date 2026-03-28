import ollama
import difflib
import re
from transformers import pipeline

# --- CONFIGURATION ---
# We use DistilBART for Zero-Shot: It's fast and doesn't need training for new labels.
INTENT_MODEL = "cross-encoder/nli-MiniLM2-L6-H768"
# Standard NER for identifying locations and miscellaneous entities
NER_MODEL = "dslim/bert-base-NER"
LLM_MODEL = "llama3.2:1b-instruct-q4_K_M"

AVAILABLE_MUSIC = ["jazz_vibes.wav", "rock_anthem.wav", "lofi_beats.wav", "outer_wilds.wav", "zelda.wav"]
INTENT_LABELS = ["music", "weather", "light", "talk", "message", "task", "timer"]
DEFAULT_LOCATION = "Paris"

print("Loading Neural Networks...")
classifier = pipeline(
    "zero-shot-classification", 
    model=INTENT_MODEL, 
    device=-1,
    model_kwargs={"tie_word_embeddings": False}
)
ner_tagger = pipeline(
    "ner", 
    model=NER_MODEL, 
    aggregation_strategy="simple", 
    device=-1,
    model_kwargs={"tie_word_embeddings": False}
)  # ty:ignore[no-matching-overload]

def get_entities(text):
    """Uses NER to extract recognizable elements."""
    entities = ner_tagger(text)
    results = {"LOC": None, "MISC": None, "PER": None, "ORG": None}
    for ent in entities:
        if ent['entity_group'] in results:
            results[ent['entity_group']] = ent['word']
    return results

def get_llm_chat(text):
    """Fallback to OLlama for chat responses."""
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
        entities = get_entities(text)
        search_term = entities['MISC'] if entities['MISC'] else text
        match = difflib.get_close_matches(search_term, AVAILABLE_MUSIC, n=1, cutoff=0.2)
        song = match[0] if match else "default.wav"
        return f'MUSIC("{song}")'

    elif intent == "weather":
        entities = get_entities(text)
        city = entities['LOC'] if entities['LOC'] else DEFAULT_LOCATION
        return f'WEATHER("{city}")'

    elif intent == "light":
        state = "ON" if "on" in text.lower() else "OFF"
        return f'LIGHT("{state}")'

    elif intent == "message":
        entities = get_entities(text)
        if entities['PER']:
             dest = entities['PER']
        else:
            return f'ERROR(Message destination not found)' 
        if entities['ORG']:
             app = entities['ORG']
        else:
            return f'ERROR(Messaging application not found)' 
        state = "ON" if "on" in text.lower() else "OFF"
        return f'MESSAGE("{dest}","{app}")'

    else: # intent == "talk"
        response = get_llm_chat(text)
        return f'CHAT("{response}")'

# --- TEST SUITE ---
if __name__ == "__main__":
    tests = [
        "Play the rock anthem",
        "Is it raining in San Francisco?",
        "Turn the lights on please",
        "Tell me a short joke",
        "Send a message to Antoine ROGER on WhatsApp"
    ]
    for t in tests:
        print(f"COMMAND: {process_request(t)}")

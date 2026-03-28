import difflib
from transformers import pipeline

DEFAULT_LOCATION = "Paris"
DEFAULT_MUSIC = "outer_wilds.wav"

INTENT_MODEL = "cross-encoder/nli-MiniLM2-L6-H768"
NER_MODEL = "dslim/bert-base-NER"
LLM_MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
INTENT_LABELS = ["chat", "music", "task", "timer", "weather"]

# TODO replace with dynamic list
AVAILABLE_MUSIC = ["jazz_vibes.wav", "rock_anthem.wav", "lofi_beats.wav", "outer_wilds.wav", "zelda.wav"]

print("Loading Neural Networks...")
classifier = pipeline("zero-shot-classification", model=INTENT_MODEL, device=-1)
ner_tagger = pipeline("ner", model=NER_MODEL, aggregation_strategy="simple", device=-1)  # ty:ignore[no-matching-overload]
chatbot = pipeline("text-generation", model=LLM_MODEL, device=-1, max_length=80)

def get_entities(text):
    entities = ner_tagger(text)
    results = {"LOC": None, "MISC": None}
    for ent in entities:
        if ent['entity_group'] in results and results[ent['entity_group']] is None:
            results[ent['entity_group']] = ent['word']
    return results

def get_llm_chat(text):
    messages = [
        {"role": "system", "content": "You are a tiny robot. Keep answers under 15 words."},
        {"role": "user", "content": text}
    ]
    result = chatbot(messages)
    return result[0]["generated_text"][-1]["content"].strip()

def process_request(text):
    print(f"\nProcessing: '{text}'")

    intent_res = classifier(text, candidate_labels=INTENT_LABELS)
    intent = intent_res['labels'][0]
    confidence = intent_res['scores'][0]
    print(f"Intent: {intent} ({confidence:.2f})")

    if confidence < 0.5:
        return f'CHAT("{get_llm_chat(text)}")'

    if intent == "music":
        entities = get_entities(text)
        search_term = entities['MISC'] if entities['MISC'] else text
        match = difflib.get_close_matches(search_term, AVAILABLE_MUSIC, n=1, cutoff=0.2)
        return f'MUSIC("{match[0] if match else DEFAULT_MUSIC}")'

    elif intent == "task":
        return f'TASK("test")'

    elif intent == "timer":
        return f'TIMER("test")'

    elif intent == "weather":
        entities = get_entities(text.title())
        location = entities['LOC'] if entities['LOC'] else DEFAULT_LOCATION
        return f'WEATHER("{location}")'

    else:
        return f'CHAT("{get_llm_chat(text)}")'

if __name__ == "__main__":
    tests = [
        "Play the rock anthem",
        "I want to listen to my outer wild song",
        "Is it raining in San Francisco?",
        "Is it raining in montreal?",
        "Tell me a short joke",
        "Set a 5 minutes timer",
        "Add an item to my todo list",
        "Tell me about thermodynamics",
        "tell me who won the 1998 and 2002 world cups"
    ]
    for t in tests:
        print(f"Command: {process_request(t)}")

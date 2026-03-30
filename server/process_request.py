import difflib
from transformers import pipeline
from weather import get_weather
from chat import get_answer

DEFAULT_LOCATION = "Paris"
DEFAULT_MUSIC = "outer_wilds.wav"

INTENT_MODEL = "cross-encoder/nli-MiniLM2-L6-H768"
NER_MODEL = "dslim/bert-base-NER"
INTENT_LABELS = ["explain", "music", "reminder", "timer", "weather"]

# TODO replace with dynamic list
AVAILABLE_MUSIC = ["jazz_vibes.wav", "rock_anthem.wav", "lofi_beats.wav", "outer_wilds.wav", "zelda.wav"]

print("Loading Neural Networks...")
classifier = pipeline("zero-shot-classification", model=INTENT_MODEL, device=-1)
ner_tagger = pipeline("ner", model=NER_MODEL, aggregation_strategy="simple", device=-1)  # ty:ignore[no-matching-overload]

def get_entities(text):
    entities = ner_tagger(text)
    results = {"LOC": None, "MISC": None}
    for ent in entities:
        if ent['entity_group'] in results and results[ent['entity_group']] is None:
            results[ent['entity_group']] = ent['word']
    return results

def process_request(text):
    print(f"\nProcessing: '{text}'")

    intent_res = classifier(text, candidate_labels=INTENT_LABELS)
    intent = intent_res['labels'][0]
    confidence = intent_res['scores'][0]
    print(f"Intent: {intent} ({confidence:.2f})")

    if confidence < 0.5:
        return get_answer(text)

    if intent == "music":
        entities = get_entities(text)
        search_term = entities['MISC'] if entities['MISC'] else text
        match = difflib.get_close_matches(search_term, AVAILABLE_MUSIC, n=1, cutoff=0.2)
        return f'MUSIC("{match[0] if match else DEFAULT_MUSIC}")'

    elif intent == "reminder":
        task = text.split(" to ")[1]
        return f'REMIND("{task}")'

    elif intent == "timer":
        unit = "M"
        value = 5
        if "second" in text.lower():
            unit = "S"
        if "hour" in text.lower():
            unit = "H"
        for word in text.split():
            if word.isdigit():
                value = word
        return f'TIMER("{value} {unit}")'

    elif intent == "weather":
        entities = get_entities(text.title())
        location = entities['LOC'] if entities['LOC'] else DEFAULT_LOCATION
        return get_weather(location)

    else:
        return get_answer(text)

if __name__ == "__main__":
    tests = [
        "Play the rock anthem",
        "I want to listen to my outer wild song",
        "Is it raining in San Francisco?",
        "Is it raining in montreal?",
        "Tell me a short joke",
        "Set a 5 minutes timer",
        "Set a 25 second timer",
        "Set a 10 hours timer",
        "Remind me to call mom",
        "explain thermodynamics",
        "who won the 1998 and 2002 football world cups"
    ]
    for t in tests:
        lines = process_request(t)
        for line in lines:
            print(line)

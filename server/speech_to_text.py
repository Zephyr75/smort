from word2number import w2n
import re
from transformers import pipeline

whisper = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base",
    device=-1
)

def transcribe(audio_path: str) -> str:
    result = whisper(audio_path)
    return result["text"].strip()

def extract_number(text: str):
    """Converts either '5' or 'five' to an int/float."""
    # Try plain numerals first
    match = re.search(r'\d+\.?\d*', text)
    if match:
        return float(match.group())
    
    # Extract just the number words from the sentence, then convert
    number_pattern = r'\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|' \
                     r'eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|' \
                     r'eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|' \
                     r'eighty|ninety|hundred|thousand)(?:\s+(?:zero|one|two|three|' \
                     r'four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|' \
                     r'fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|' \
                     r'thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand))*\b'
    
    match = re.search(number_pattern, text, flags=re.IGNORECASE)
    if match:
        try:
            return float(w2n.word_to_num(match.group()))
        except:
            return None
    
    return None

# Example usage
text = transcribe("5min.wav")
print(text)

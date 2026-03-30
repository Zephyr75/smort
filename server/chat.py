from aiohttp.web_routedef import get
import textwrap
from transformers import pipeline

LLM_MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
WIDTH = 20
ROWS = 4

chatbot = pipeline("text-generation", model=LLM_MODEL, device=-1, max_new_tokens=80)

def format_lcd(text):
    lines = textwrap.wrap(text, WIDTH)
    lines = lines[:ROWS]
    lines = [l.ljust(WIDTH) for l in lines]
    return lines

def get_answer(question):
    messages = [
        {"role": "system", "content": "You are a tiny robot. Keep answers under 15 words."},
        {"role": "user", "content": question}
    ]
    result = chatbot(messages)
    result = result[0]["generated_text"][-1]["content"].strip()
    return format_lcd(result)

if __name__ == "__main__":
    question = input("Question: ")
    for line in get_answer(question):
        print(line)

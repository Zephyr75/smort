from main import process_voice_text
import time

test_scenarios = [
    "Tell me a joke about robots",                  # Expected: CHAT
    "What's the weather in London?",                # Expected: WEATHER
    "Too dark in here",                             # Expected: LIGHT
    "How is the weather in Berlin?",                # Expected: WEATHER
    "Play some rock music",                         # Expected: MUSIC
    "Turn off the lights",                          # Expected: LIGHT
    "I need a lo-fi track for focusing"             # Expected: MUSIC
]

def run_tests():
    print("🚀 Running Improved Brain Test Suite...")
    print("-" * 50)
    for scenario in test_scenarios:
        start = time.time()
        results = process_voice_text(scenario)
        end = time.time()
        print(f"Input: {scenario}")
        print(f"  Result: {results[0]} | Time: {end-start:.2f}s\n")

if __name__ == "__main__":
    run_tests()

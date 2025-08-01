import requests
import json
from bs4 import BeautifulSoup

# Load URLs
with open("gameurls.json", "r") as f:
    urls = json.load(f)

# Classes used to identify player count element
target_classes = [
    "bg-gradient-to-r",
    "from-[#93E560]",
    "to-[#60E5C5]",
    "bg-clip-text",
    "leading-snug",
    "text-transparent",
    "[-webkit-text-fill-color:transparent]",
    "[text-fill-color:transparent]"
]

# Helper function to check class match
def has_all_classes(tag):
    return tag.has_attr("class") and all(c in tag["class"] for c in target_classes)

# Store results as a list of tuples (url, player_count)
results = []

for url in urls:
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        element = soup.find(has_all_classes)

        if element:
            text = element.get_text(strip=True).replace(",", "")
            # Attempt to parse player count
            try:
                count = int(text)
                results.append((url, count))
            except ValueError:
                print(f"Couldn't parse count from {url}: '{text}'")
        else:
            print(f"No matching element in {url}")
    except Exception as e:
        print(f"Error processing {url}: {e}")

# Sort by player count descending
sorted_results = sorted(results, key=lambda x: x[1], reverse=True)

# Output
print("\nSorted Game List by Player Count:")
for url, count in sorted_results:
    print(f"{count:,} players - {url}")

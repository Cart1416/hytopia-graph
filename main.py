from flask import Flask, render_template, jsonify
import threading, time, requests, json
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "data.json"
URLS_FILE = "gameurls.json"
UPDATE_INTERVAL = 300  # 5 minutes

# Tailwind-style class list to locate the player count
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

def has_all_classes(tag):
    return tag.has_attr("class") and all(c in tag["class"] for c in target_classes)

# Periodic background scraper
def fetch_and_store():
    while True:
        with open(URLS_FILE) as f:
            urls = json.load(f)

        new_data = {}
        timestamp = datetime.now().strftime("%m/%d/%y %I:%M %p")

        for url in urls:
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                element = soup.find(has_all_classes)
                count = int(element.get_text(strip=True).replace(",", ""))
                # Find totalPlaysCount using a simple text search
                html_text = response.text
                try:
                    match_start = html_text.index('totalPlaysCount\\",') + len('totalPlaysCount\\",')
                    match_end = html_text.index(',', match_start)
                    total_plays = int(html_text[match_start:match_end])
                except:
                    total_plays = None
                slug = url.rstrip("/").split("/")[-1]
                new_data[slug] = {
                    "current": count,
                    "total": total_plays
                }
            except:
                pass  # skip broken pages

        # Load existing data or init
        try:
            with open(DATA_FILE, "r") as f:
                all_data = json.load(f)
        except:
            all_data = {"timestamps": [], "games": {}}

        all_data["timestamps"].append(timestamp)

        for slug, count in new_data.items():
            all_data["games"].setdefault(slug, []).append(count)

        with open(DATA_FILE, "w") as f:
            json.dump(all_data, f, indent=2)
            print(f"Data updated at {timestamp}")

        time.sleep(UPDATE_INTERVAL)

# Start background scraping thread
threading.Thread(target=fetch_and_store, daemon=True).start()

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/totals")
def totals():
    return render_template("totals.html")

@app.route("/data")
def data():
    try:
        with open(DATA_FILE) as f:
            return jsonify(json.load(f))
    except:
        return jsonify({})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

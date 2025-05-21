from flask import Flask, jsonify
from scraper import scrape_newegg, scrape_ebay

app = Flask(__name__)

@app.route('/')
def hello():
    # Test that scraper is being imported correctly
    return jsonify({"status": "ok", "message": "Flask app with scraper imported"})

if __name__ == "__main__":
    app.run(debug=True)

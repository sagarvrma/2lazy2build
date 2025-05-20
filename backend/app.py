from flask import Flask, request, jsonify, send_from_directory
from scraper import scrape_newegg, scrape_ebay
import os

app = Flask(__name__)

@app.route("/scrape")
def scrape():
    cpu_param = request.args.get("cpu", "")
    gpu_param = request.args.get("gpu", "")
    max_price = request.args.get("max_price", type=float)
    in_stock = request.args.get("in_stock", "false").lower() == "true"
    refurbished = request.args.get("refurbished", "false").lower() == "true"
    min_ram = request.args.get("min_ram", type=int)
    min_storage = request.args.get("min_storage", type=int)

    cpu_list = [c.strip() for c in cpu_param.split(",") if c.strip()]
    gpu_list = [g.strip() for g in gpu_param.split(",") if g.strip()]

    results = scrape_newegg(
        cpu_list=cpu_list,
        gpu_list=gpu_list,
        max_price=max_price,
        filter_in_stock=in_stock,
        filter_refurb=refurbished,
        min_ram=min_ram,
        min_storage=min_storage
    )

    ebay_results = scrape_ebay(
        cpu_list=cpu_list,
        gpu_list=gpu_list,
        max_price=max_price,
        min_seller_rating=98,
        filter_refurb=refurbished,
        min_ram=min_ram,
        min_storage=min_storage
    )

    return jsonify(results + ebay_results)

# Serve logo images (e.g., /static/logos/hp.png)
@app.route("/static/logos/<path:filename>")
def serve_logo(filename):
    return send_from_directory(os.path.join("static", "logos"), filename)

if __name__ == "__main__":
    app.run(debug=True)

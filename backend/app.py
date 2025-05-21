import logging
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from scraper import scrape_newegg, scrape_ebay
import os
from serverless_wsgi import handle_request  # Required for Vercel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/scrape")
def scrape():
    print("🔵 /scrape route hit")
    try:
        cpu_param = request.args.get("cpu", "")
        gpu_param = request.args.get("gpu", "")
        max_price = request.args.get("max_price", type=float)
        in_stock = request.args.get("in_stock", "false").lower() == "true"
        refurbished = request.args.get("refurbished", "false").lower() == "true"
        min_ram = request.args.get("min_ram", type=int)
        min_storage = request.args.get("min_storage", type=int)

        cpu_list = [c.strip() for c in cpu_param.split(",") if c.strip()]
        gpu_list = [g.strip() for g in gpu_param.split(",") if g.strip()]

        print(f"🧪 Params: CPU={cpu_list}, GPU={gpu_list}")

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

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error in scraping: {str(e)}\n{error_details}")
        return jsonify({"error": str(e), "details": error_details}), 500

@app.route("/static/logos/<path:filename>")
def serve_logo(filename):
    logos_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "logos"))
    return send_from_directory(logos_dir, filename)

def lambda_handler(event, context):
    return handle_request(app, event, context)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

import logging
import traceback
import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from serverless_wsgi import handle_request  # Import serverless-wsgi to wrap the app for Vercel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    logger.info(f"Added current directory to path: {current_dir}")

# Now try the import with extensive error handling
try:
    from scraper import scrape_newegg, scrape_ebay
    logger.info("Successfully imported scraper module")
except ImportError as e:
    error_message = f"Failed to import scraper: {e}"
    logger.error(error_message)
    
    # Log directory contents to help debug
    try:
        logger.error(f"Files in current directory: {os.listdir(current_dir)}")
        
        # Check if scraper.py exists
        scraper_path = os.path.join(current_dir, "scraper.py")
        if os.path.exists(scraper_path):
            logger.error(f"scraper.py exists at: {scraper_path}")
            # Check file size to ensure it's not empty
            logger.error(f"scraper.py size: {os.path.getsize(scraper_path)} bytes")
        else:
            logger.error(f"scraper.py DOES NOT exist at: {scraper_path}")
    except Exception as dir_error:
        logger.error(f"Error checking directory contents: {dir_error}")
    
    # Attempt alternate import strategies
    try:
        # Try to import using full path
        import importlib.util
        spec = importlib.util.spec_from_file_location("scraper", os.path.join(current_dir, "scraper.py"))
        if spec:
            scraper = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(scraper)
            scrape_newegg = scraper.scrape_newegg
            scrape_ebay = scraper.scrape_ebay
            logger.info("Successfully imported scraper using importlib")
        else:
            logger.error("Failed to load scraper spec using importlib")
    except Exception as import_error:
        logger.error(f"Alternative import also failed: {import_error}")
        # Re-raise the original error if all attempts fail
        raise ImportError(f"Could not import scraper module: {e}")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/")
def index():
    """Root endpoint to verify the app is running"""
    return jsonify({
        "status": "ok",
        "message": "Flask app is running correctly"
    })

@app.route("/debug")
def debug():
    """Debug endpoint to check environment and files"""
    import sys
    
    # Check file system and environment
    return jsonify({
        "python_version": sys.version,
        "current_directory": os.getcwd(),
        "script_directory": os.path.dirname(os.path.abspath(__file__)),
        "files_in_current_dir": os.listdir(os.getcwd()),
        "files_in_script_dir": os.listdir(os.path.dirname(os.path.abspath(__file__))),
        "scraper_exists": os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraper.py")),
        "python_path": sys.path
    })

@app.route("/scrape")
def scrape():
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

        # Log parameters received
        logger.info(f"Scraping with params: CPU={cpu_list}, GPU={gpu_list}, max_price={max_price}")

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

        # Log success
        logger.info(f"Scraping completed successfully. Found {len(results)} Newegg results and {len(ebay_results)} eBay results")
        return jsonify(results + ebay_results)

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error in scraping: {str(e)}\n{error_details}")
        return jsonify({"error": str(e), "details": error_details}), 500

@app.route("/static/logos/<path:filename>")
def serve_logo(filename):
    logos_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "logos"))
    logger.info(f"Serving logo from: {logos_dir}/{filename}")
    return send_from_directory(logos_dir, filename)

# This is required for Vercel to handle the function correctly
def lambda_handler(event, context):
    return handle_request(app, event, context)

# For local testing, we can still run it normally
if __name__ == "__main__":
    app.run(debug=True)
import re
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def extract_condition(title_lower):
    if "refurb" in title_lower:
        return "refurbished"
    if "used" in title_lower:
        return "used"
    return "new"

def extract_ram(title):
    match = re.search(r"(\d+)\s*GB\s*(DDR\d)?", title, re.IGNORECASE)
    if not match:
        match = re.search(r"(\d+)[\s\-]?(gb|g\.b\.|gigs)[\s\-]?(ram|memory)?", title, re.IGNORECASE)
    return int(match.group(1)) if match else None

def extract_storage(title):
    title = title.lower()
    pattern = r"(?:\b(\d+)\s*(tb|gb|t|g)\b\s*(ssd|hdd|nvme|m\.2|pcie)?|(?:ssd|hdd|nvme|m\.2|pcie)\s*(\d+)\s*(tb|gb|t|g))"
    matches = re.findall(pattern, title)
    valid = []
    for m in matches:
        if m[0] and m[1]:
            size = int(m[0])
            unit = m[1]
        elif m[3] and m[4]:
            size = int(m[3])
            unit = m[4]
        else:
            continue
        if unit in ["tb", "t"]:
            size_gb = size * 1024
        else:
            size_gb = size
        valid.append(size_gb)
    return max(valid) if valid else None

def match_component(title_lower, options):
    title_lower = title_lower.lower()
    noise_words = ["intel", "amd", "nvidia", "geforce", "core", "graphics", "desktop", "laptop", "computer"]
    for word in noise_words:
        title_lower = title_lower.replace(word, " ")
    title_lower = re.sub(r"(?<=\d)(?=[a-z])", " ", title_lower)
    title_lower = re.sub(r"[^a-z0-9\s]", " ", title_lower)
    title_tokens = re.sub(r"\s+", " ", title_lower).strip().split()
    title_token_str = " ".join(title_tokens)
    
    for option in options:
        option_clean = option.lower()
        for word in noise_words + ["rtx"]:
            option_clean = option_clean.replace(word, " ")
        option_clean = re.sub(r"\s+", " ", option_clean).strip()
        
        # Enhanced CPU matching for Intel processors
        if option_clean in ["i7", "i5", "i9"]:
            # Match variations like "i7-14700", "core i7", "i7 14th", etc.
            # But ONLY for the specific CPU type selected (i7 matches i7 variants, not i5 or i9)
            patterns = [
                f" {option_clean} ",           # exact match: " i7 "
                f" {option_clean}-",           # i7-14700
                f" {option_clean}\\d",         # i714700  
                f"{option_clean}-\\d",         # i7-14
                f"{option_clean}\\s+\\d",      # i7 14
            ]
            
            for pattern in patterns:
                if re.search(pattern, f" {title_token_str} "):
                    return option
        else:
            # Original matching for other components
            if f" {option_clean} " in f" {title_token_str} ":
                return option
    return None

def clean_price_string(price):
    match = re.search(r"\$[\d,]+(\.\d+)?", price)
    return float(match.group(0).replace("$", "").replace(",", "")) if match else None

def extract_brand(title):
    title = title.lower()
    # Remove the word 'refurbished' from the title if it's present
    title = title.replace("refurbished", "").strip()
    
    title_tokens = title.split()
    if not title_tokens:
        return None
    
    # Check if the first token is a known brand or a prefix
    if title_tokens[0] in ["gaming", "desktop", "pc", "computer"]:
        return " ".join(title_tokens[:2])
    
    # Return the first token as the brand
    return title_tokens[0]

def classify_device_type(title):
    # Convert the title to lowercase for easier matching
    title_lower = title.lower()

    # Keywords for laptops and desktops
    laptop_keywords = ["laptop"]
    desktop_keywords = ["desktop", "tower", "pc", "gaming pc", "all-in-one"]

    # Check if both laptop and desktop keywords exist
    if any(keyword in title_lower for keyword in laptop_keywords) and any(keyword in title_lower for keyword in desktop_keywords):
        return "unknown"  # Ignore listings with both laptop and desktop keywords

    # Check if the title mentions a laptop
    if any(keyword in title_lower for keyword in laptop_keywords):
        return "laptop"

    # Check if the title mentions a desktop
    if any(keyword in title_lower for keyword in desktop_keywords):
        return "desktop"

    # Default to unknown if no keyword matches
    return "unknown"

def scrape_newegg(cpu_list, gpu_list, max_price, filter_in_stock=False, filter_refurb=False, min_ram=None, min_storage=None):
    # TODO: Newegg scraping temporarily disabled due to anti-bot protection
    # Working on implementing proxy rotation and advanced anti-bot bypassing
    print("⚠️ Newegg scraping in development - anti-bot protection bypass in progress")
    return []

    # NEWEGG SCRAPER - TEMPORARILY COMMENTED OUT
    # Will be re-enabled once anti-bot protection is resolved
    """
    items = []
    with sync_playwright() as p:
        # Use more realistic browser settings
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        # Add extra headers to look more like a real browser
        page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        for cpu in cpu_list:
            for gpu in gpu_list:
                query = f"{cpu} {gpu}".replace(" ", "+")
                url = f"https://www.newegg.com/p/pl?d={query}"
                
                try:
                    print(f"🔄 Trying Newegg: {url}")
                    
                    # Navigate with longer timeout
                    page.goto(url, timeout=120000, wait_until='networkidle')
                    
                    # Add random delay to seem more human
                    page.wait_for_timeout(3000 + (hash(query) % 3000))
                    
                    # Try multiple selectors in case they changed
                    selectors_to_try = [
                        ".item-cell, .item-container",
                        ".item-wrap",
                        "[data-testid='item-cell']",
                        ".item-info"
                    ]
                    
                    results_found = False
                    for selector in selectors_to_try:
                        try:
                            page.wait_for_selector(selector, timeout=15000)
                            results_found = True
                            print(f"✅ Found elements with selector: {selector}")
                            break
                        except:
                            print(f"❌ Selector failed: {selector}")
                            continue
                    
                    if not results_found:
                        print(f"⚠️ No results found with any selector for: {url}")
                        continue
                        
                    # Wait a bit more for dynamic content
                    page.wait_for_timeout(5000)
                    html = page.content()
                    
                except Exception as e:
                    print(f"❌ Newegg failed for {query}: {e}")
                    continue
                
                soup = BeautifulSoup(html, "html.parser")
                results = soup.select(".item-cell, .item-container")
                print(f"📦 Scraped {len(results)} items from: {url}")
                
                if not results:
                    # Try alternative selectors
                    results = soup.select(".item-wrap") or soup.select("[data-testid='item-cell']")
                    print(f"📦 Alternative scraping found {len(results)} items")
                
                if not results:
                    continue
                    
                for item in results:
                    title_elem = item.select_one(".item-title")
                    price_elem = item.select_one(".price-current")
                    stock_elem = item.select_one(".item-promo")
                    img_elem = item.select_one("img")
                    image_url = img_elem["src"] if img_elem and "src" in img_elem.attrs else None
                    
                    # Extract and clean title
                    title = title_elem.get_text(strip=True) if title_elem else "No title"
                    title = title.replace("refurbished", "").strip()
                    title = " ".join(title.split())
                    
                    # Classify as laptop or desktop
                    device_type = classify_device_type(title)

                    price = price_elem.get_text(strip=True) if price_elem else "N/A"
                    link = title_elem["href"] if title_elem else None
                    in_stock = not ("OUT OF STOCK" in stock_elem.get_text(strip=True).upper() if stock_elem else False)
                    condition = extract_condition(title.lower())
                    matched_cpu = match_component(title.lower(), cpu_list)
                    matched_gpu = match_component(title.lower(), gpu_list)
                    
                    print(f"- Title: {title}")
                    print(f"  CPU match: {matched_cpu}, GPU match: {matched_gpu}, Price: {price}")
                    if not matched_cpu or not matched_gpu:
                        print("  ❌ Skipped: No CPU or GPU match")
                        continue
                    numeric_price = clean_price_string(price)
                    if not numeric_price:
                        print("  ❌ Skipped: Invalid price format")
                        continue
                    if numeric_price < 300 or (max_price and numeric_price > float(max_price)):
                        print("  ❌ Skipped: Price filter")
                        continue
                    ram_gb = extract_ram(title)
                    storage_gb = extract_storage(title)
                    if filter_in_stock and not in_stock:
                        print("  ❌ Skipped: Out of stock")
                        continue
                    if filter_refurb and condition != "refurbished":
                        print("  ❌ Skipped: Not refurbished")
                        continue
                    if min_ram and (ram_gb is None or ram_gb < min_ram):
                        print("  ❌ Skipped: RAM too low")
                        continue
                    if min_storage and (storage_gb is None or storage_gb < min_storage):
                        print("  ❌ Skipped: Storage too low")
                        continue
                    
                    # Add the device type to the JSON object
                    items.append({
                        "title": title,
                        "brand": extract_brand(title),
                        "price": price,
                        "link": link,
                        "image": image_url,
                        "in_stock": in_stock,
                        "refurbished": condition == "refurbished",
                        "condition": condition,
                        "matched_cpu": matched_cpu,
                        "matched_gpu": matched_gpu,
                        "ram_gb": ram_gb,
                        "storage_gb": storage_gb,
                        "device_type": device_type,
                        "source": "Newegg"
                    })
        browser.close()
    return items
    """

def scrape_ebay(cpu_list, gpu_list, max_price=None, min_seller_rating=98, filter_refurb=False, min_ram=None, min_storage=None):
    items = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0")
        page = context.new_page()

        for gpu_query in gpu_list:
            search_query = gpu_query.replace(" ", "+")
            url = f"https://www.ebay.com/sch/i.html?_nkw={search_query}+prebuilt&_sacat=0&_from=R40&_sop=12"

            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector(".s-item", timeout=10000)
                html = page.content()
            except Exception as e:
                print(f"❌ eBay request failed for {gpu_query}: {e}")
                continue

            soup = BeautifulSoup(html, "html.parser")

            for card in soup.select("li.s-item"):
                title_elem = card.select_one(".s-item__title")
                price_elem = card.select_one(".s-item__price")
                link_elem = card.select_one("a.s-item__link")
                seller_elem = card.select_one(".s-item__seller-info-text, .s-item__etrs-text")
                img_elem = card.select_one(".s-item__image img")

                if not all([title_elem, price_elem, link_elem]):
                    continue

                title = title_elem.get_text(strip=True)
                title_lower = title.lower()

                device_type = classify_device_type(title)
                price = price_elem.get_text(strip=True)
                link = link_elem["href"]
                condition = extract_condition(title_lower)
                matched_cpu = match_component(title_lower, cpu_list)
                matched_gpu = match_component(title_lower, gpu_list)

                print(f"- eBay Title: {title}")
                print(f"  CPU match: {matched_cpu}, GPU match: {matched_gpu}, Price: {price}")

                if not matched_cpu or not matched_gpu:
                    print("  ❌ Skipped: No CPU or GPU match")
                    continue

                numeric_price = clean_price_string(price)
                if not numeric_price:
                    print("  ❌ Skipped: Invalid price format")
                    continue
                if numeric_price < 300 or (max_price and numeric_price > float(max_price)):
                    print("  ❌ Skipped: Price filter")
                    continue
                if filter_refurb and condition != "refurbished":
                    print("  ❌ Skipped: Not refurbished")
                    continue

                seller_ok = True
                if seller_elem:
                    match = re.search(r"(\d+(\.\d+)?)%", seller_elem.get_text())
                    if match:
                        rating = float(match.group(1))
                        seller_ok = rating >= min_seller_rating
                if not seller_ok:
                    print("  ❌ Skipped: Seller rating too low")
                    continue

                ram_gb = extract_ram(title)
                storage_gb = extract_storage(title)
                if min_ram and (ram_gb is None or ram_gb < min_ram):
                    print("  ❌ Skipped: RAM too low")
                    continue
                if min_storage and (storage_gb is None or storage_gb < min_storage):
                    print("  ❌ Skipped: Storage too low")
                    continue

                brand = extract_brand(title)
                brand_lower = brand.lower()
                if brand_lower in ["gaming", "computer", "pc", "desktop", "gaming computer"]:
                    brand = "Generic"
                    brand_lower = "generic"

                # Extract actual product image from eBay listing
                image_url = None
                if img_elem and img_elem.get("src"):
                    image_url = img_elem["src"]
                    # eBay sometimes uses data-src for lazy loading
                    if not image_url or "placeholder" in image_url.lower():
                        if img_elem.get("data-src"):
                            image_url = img_elem["data-src"]
                
                # Fallback to brand logos if no product image found
                if not image_url or "placeholder" in image_url.lower():
                    logo_sources = {
                        "msi": "https://1000logos.net/wp-content/uploads/2018/10/MSI-Logo-500x281.png",
                        "hp": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/HP_logo_2012.svg/2048px-HP_logo_2012.svg.png",
                        "dell": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Dell_Logo.svg/300px-Dell_Logo.svg.png",
                        "acer": "https://static.vecteezy.com/system/resources/previews/019/766/411/non_2x/acer-logo-acer-icon-transparent-free-png.png",
                        "asus": "https://cdn.freebiesupply.com/logos/large/2x/asus-6630-logo-png-transparent.png",
                        "cyberpowerpc": "https://1000logos.net/wp-content/uploads/2020/09/CyberPowerPC-Logo.jpg",
                        "ibuypower": "https://edgeup.asus.com/wp-content/uploads/2015/04/iBuyPower-Logo-resized.jpg",
                    }
                    image_url = logo_sources.get(brand_lower, "https://2lazy2build.vercel.app/static/logos/generic.png")

                items.append({
                    "title": title,
                    "brand": brand,
                    "price": price,
                    "link": link,
                    "image": image_url,
                    "refurbished": condition == "refurbished",
                    "condition": condition,
                    "matched_cpu": matched_cpu,
                    "matched_gpu": matched_gpu,
                    "ram_gb": ram_gb,
                    "storage_gb": storage_gb,
                    "device_type": device_type,
                    "source": "eBay"
                })

        browser.close()
    return items
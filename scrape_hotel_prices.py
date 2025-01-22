from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime, timedelta
import time

def get_next_days():
    today = datetime.today()
    dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    return dates

def get_hotel_names():
    return [
        "ibis Melbourne - Glen Waverley", 
        "Hotel Chadstone Melbourne, MGallery",
        "Avani Melbourne Box Hill Residences",
        "Yarra Valley Motel",
        "The Waverley International Hotel"
    ]

def main():
    hotel_names = get_hotel_names()

    if not hotel_names:
        print("No hotel names entered. Exiting.")
        return

    with sync_playwright() as p:
        dates = get_next_days()
        price_data = []
        browser = p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-gpu", "--start-maximized", "--window-size=1920x1080"]
        )  # Run headless with options
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )  # Set a real user-agent
        page = context.new_page()

        for checkin_date in dates:
            checkout_date = (datetime.strptime(checkin_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            row_data = {'Check_in': checkin_date, 'Check_out': checkout_date}

            for hotel_name in hotel_names:
                page_url = f'https://www.booking.com/searchresults.en-us.html?checkin={checkin_date}&checkout={checkout_date}&selected_currency=SGD&ss={hotel_name}&ssne={hotel_name}&ssne_untouched={hotel_name}&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_type=city&group_adults=1&no_rooms=1&group_children=0&sb_travel_purpose=leisure'

                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        page.goto(page_url, wait_until="domcontentloaded")  # Wait for DOMContentLoaded event
                        time.sleep(3)  # Optional: Wait for dynamic content to load

                        # Ensure the price element is available
                        page.wait_for_selector('//div[@data-testid="property-card"]', timeout=10000)  # Wait for property cards
                        hotel = page.locator('//div[@data-testid="property-card"]').first

                        price = hotel.locator('//span[@data-testid="price-and-discounted-price"]').inner_text()
                        row_data[f'{hotel_name}'] = price
                        break  # Exit the retry loop if successful
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"Attempt {attempt + 1} failed for {hotel_name} on {checkin_date}: {e}. Refreshing page...")
                            page.reload()
                            time.sleep(1)
                        else:
                            row_data[f'{hotel_name}'] = 'N/A'
                            print(f"Error extracting price for {hotel_name} on {checkin_date}: {e}")

            price_data.append(row_data)

        df = pd.DataFrame(price_data)
        df.to_excel('daily_price_multiple_hotels.xlsx', index=False)

        browser.close()

if __name__ == '__main__':
    main()

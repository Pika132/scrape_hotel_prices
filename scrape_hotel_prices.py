import tkinter as tk
from tkinter import messagebox  
from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime, timedelta
import time

def get_next_days():
    today = datetime.today()
    dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    return dates

def get_hotel_names():
    # Return a fixed list of hotel names
    return [
        "ibis Melbourne - Glen Waverley",
        "Oros Hotel and Apartments",
        "Art Series - The Chen",
        "Rydges Ringwood",
        "Hotel Chadstone Melbourne, MGallery"
    ]

def main():
    hotel_names = get_hotel_names()

    if not hotel_names:
        print("No hotel names entered. Exiting.")
        return

    with sync_playwright() as p:
        dates = get_next_days()
        price_data = []
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for checkin_date in dates:
            checkout_date = (datetime.strptime(checkin_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            row_data = {'Check_in': checkin_date, 'Check_out': checkout_date}

            for hotel_name in hotel_names:
                page_url = f'https://www.booking.com/searchresults.en-us.html?checkin={checkin_date}&checkout={checkout_date}&selected_currency=SGD&ss={hotel_name}&ssne={hotel_name}&ssne_untouched={hotel_name}&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_type=city&group_adults=1&no_rooms=1&group_children=0&sb_travel_purpose=leisure'

                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Shortened timeout values
                        page.goto(page_url, timeout=30000)  # 30 seconds
                        time.sleep(1)  # Shorter sleep time     

                        page.wait_for_selector('//div[@data-testid="property-card"]', timeout=5000)  # 10 seconds
                        hotel = page.locator('//div[@data-testid="property-card"]').first

                        price = hotel.locator('//span[@data-testid="price-and-discounted-price"]').inner_text()
                        row_data[f'{hotel_name}'] = price
                        break  # Exit the retry loop if successful
                    except Exception as e:
                        if attempt < max_retries - 1:  # If not the last attempt
                            print(f"Attempt {attempt + 1} failed for {hotel_name} on {checkin_date}: {e}. Refreshing page...")
                            page.reload()  # Refresh the page
                            time.sleep(1)  # Shorter wait time before retrying
                        else:
                            row_data[f'{hotel_name}'] = 'N/A'
                            print(f"Error extracting price for {hotel_name} on {checkin_date}: {e}")

            price_data.append(row_data)

        df = pd.DataFrame(price_data)
        df.to_excel('daily_price_multiple_hotels.xlsx', index=False)

        browser.close()
    
    messagebox.showinfo("Completed", "Data scraping complete and saved as 'daily_price_multiple_hotels.xlsx'.")

if __name__ == '__main__':
    main()

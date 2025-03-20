from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# --- setup chrome driver with your personal profile ---
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
# point to your personal chrome profile directory (adjust the path if needed)
chrome_options.add_argument("--user-data-dir=/Users/student/Library/Application Support/Google/Chrome")
chrome_options.add_argument("--profile-directory=Default")  # change if using a different profile

# use the chromedriver binary path (update if you moved it)
service = Service("/usr/local/bin/chromedriver/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

# --- navigate directly to the pitchbook companies search page ---
driver.get("https://my.pitchbook.com/search-results/s526028836/companies")
time.sleep(10)  # wait for the page to load; adjust as needed

all_data = []

# --- start scraping loop ---
while True:
    print("scraping current page...")
    # adjust the selector based on your page's structure
    rows = driver.find_elements(By.CSS_SELECTOR, "div.data-table__row")
    print("found", len(rows), "rows")
    
    for row in rows:
        try:
            cells = row.find_elements(By.CSS_SELECTOR, "div.custom-cell-format")
            # ensure there are enough cells in the row (11 fields needed)
            if len(cells) < 11:
                print("skipping row, not enough cells")
                continue

            company = cells[0].text
            description = cells[1].text
            industry_code = cells[2].text
            contact = cells[3].text
            contact_title = cells[4].text
            contact_email = cells[5].text
            total_raised = cells[6].text
            revenue = cells[7].text
            last_financing_date = cells[8].text
            last_financing_size = cells[9].text
            last_financing_type = cells[10].text

            all_data.append([
                company, description, industry_code, contact, contact_title,
                contact_email, total_raised, revenue, last_financing_date,
                last_financing_size, last_financing_type
            ])
        except Exception as e:
            print("error processing a row:", e)
    
    # --- pagination: click the next button ---
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
        if "disabled" in next_btn.get_attribute("class"):
            print("no more pages - next button disabled")
            break
        next_btn.click()
        print("clicked next, waiting for page to load...")
        time.sleep(10)
    except Exception as e:
        print("could not find next button or error clicking it:", e)
        break

# --- save data to csv ---
columns = [
    "Companies", "Description", "Primary Industry Code", "Primary Contact",
    "Primary Contact Title", "Primary Contact Email", "Total Raised",
    "Revenue", "Last Financing Date", "Last Financing Size",
    "Last Financing Deal Type"
]
df = pd.DataFrame(all_data, columns=columns)
df.to_csv("pitchbook_data.csv", index=False)
print("scraping complete. data saved to pitchbook_data.csv")

driver.quit()

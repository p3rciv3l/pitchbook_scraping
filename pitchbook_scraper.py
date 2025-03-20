import random
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

# --- setup chrome driver with a dedicated automation profile ---
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
# use a dedicated directory; ensure no other chrome instance uses it
chrome_options.add_argument("--user-data-dir=/Users/student/Desktop/automation_profile")
chrome_options.add_argument("--profile-directory=Default")
# set user-agent to match your regular browser
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.118 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")

service = Service("/usr/local/bin/chromedriver/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

# apply stealth settings to mimic human-like behavior
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="MacIntel",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
)

# --- navigate to the pitchbook ezproxy url ---
driver.get("https://my-pitchbook-com.ezproxy.neu.edu/")
print("please complete login/2fa/captcha manually. waiting 75 seconds...")
time.sleep(75)

# try waiting for table rows to appear; if not, allow manual retry
table_loaded = False
max_attempts = 3
attempt = 0
while attempt < max_attempts and not table_loaded:
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.data-table__row"))
        )
        table_loaded = True
        print("table loaded successfully.")
    except Exception as e:
        print("table rows not found. ensure captcha is solved and table is visible.")
        attempt += 1
        if attempt < max_attempts:
            input("press Enter to retry waiting...")
        else:
            print("table did not load after multiple attempts. exiting.")
            driver.quit()
            exit()

all_data = []

while True:
    print("scraping current page...")
    rows = driver.find_elements(By.CSS_SELECTOR, "div.data-table__row")
    print("found", len(rows), "rows on current page.")
    
    for row in rows:
        try:
            cells = row.find_elements(By.CSS_SELECTOR, "div.custom-cell-format")
            if len(cells) < 11:
                print("skipping row, not enough cells.")
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
            time.sleep(random.uniform(0.5, 1.5))  # extra random delay per row
        except Exception as e:
            print("error processing a row:", e)
    
    # --- pagination: click the next button ---
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
        if "disabled" in next_button.get_attribute("class"):
            print("next button disabled; no more pages.")
            break
        next_button.click()
        print("clicked Next, waiting for new page to load...")
        # wait until old rows become stale and new rows load
        WebDriverWait(driver, 90).until(EC.staleness_of(rows[0]))
        WebDriverWait(driver, 90).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.data-table__row"))
        )
        time.sleep(random.uniform(3, 6))  # extra delay after pagination
    except Exception as e:
        print("error during pagination or next button not found:", e)
        break

columns = [
    "Companies", "Description", "Primary Industry Code", "Primary Contact",
    "Primary Contact Title", "Primary Contact Email", "Total Raised",
    "Revenue", "Last Financing Date", "Last Financing Size",
    "Last Financing Deal Type"
]
df = pd.DataFrame(all_data, columns=columns)
df.to_csv("pitchbook_data.csv", index=False)
print("scraping complete. data saved to pitchbook_data.csv.")

driver.quit()

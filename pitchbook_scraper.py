from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# --- setup chrome driver with your personal profile ---
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
# make sure no other chrome windows using your personal profile are open
chrome_options.add_argument("--user-data-dir=/Users/student/Library/Application Support/Google/Chrome")
chrome_options.add_argument("--profile-directory=Default")

# set the path to your chromedriver binary (using the full path)
service = Service("/usr/local/bin/chromedriver/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

# --- navigate to the new pitchbook url ---
driver.get("https://my-pitchbook-com.ezproxy.neu.edu/")

print("waiting 45 seconds for you to complete 2fa/login and captcha...")
time.sleep(45)

# wait up to 90 seconds for the table rows to appear (indicating that the page has loaded)
try:
    WebDriverWait(driver, 90).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.data-table__row"))
    )
    print("table loaded successfully.")
except Exception as e:
    print("error: timed out waiting for table rows to load:", e)
    driver.quit()
    exit()

all_data = []

# --- start scraping loop ---
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
        except Exception as e:
            print("error processing a row:", e)
    
    # --- pagination: click the next button ---
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
        if "disabled" in next_button.get_attribute("class"):
            print("next button disabled, no more pages.")
            break
        next_button.click()
        print("clicked next, waiting for new page to load...")
        WebDriverWait(driver, 90).until(EC.staleness_of(rows[0]))
        WebDriverWait(driver, 90).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.data-table__row"))
        )
        time.sleep(5)
    except Exception as e:
        print("error during pagination or no next button found:", e)
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
print("scraping complete. data saved to pitchbook_data.csv.")

driver.quit()

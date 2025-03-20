from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://www.google.com")
print("page title:", driver.title)
driver.quit()

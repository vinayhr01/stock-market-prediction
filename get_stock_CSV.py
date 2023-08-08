import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import os

def get_search_suggestions(driver, userSearch):
    search = driver.find_element(By.CSS_SELECTOR, "input#yfin-usr-qry")
    search.clear()
    search.send_keys(userSearch)
    time.sleep(2)  # Wait for suggestions to appear

    li_elements = driver.find_elements(By.XPATH, "//li[@role='option']")

    # Assuming the two <div> elements are the first and second child elements within each <li> element
    company_sym = []
    span_elements = driver.find_elements(By.CSS_SELECTOR, "span.modules_quoteSpan__FveMi")

    # Extract text from span elements and store them in a list
    equi = [span_element.text for span_element in span_elements]

    for li_element in li_elements:
        div_elements = li_element.find_elements(By.TAG_NAME, 'div')
        if len(div_elements) >= 2:
            div_text_2 = div_elements[1].text
            div_text_1 = div_elements[0].text
            div_text_1 = div_text_1.replace(div_text_2, '')
            company_sym.append((div_text_2, div_text_1))

    company_sym = [i for i in company_sym if i != ('', '')]
    filtered_suggestions = [(t[0], t[1], c) for t, c in zip(company_sym, equi + ['']*(len(company_sym)-len(equi)))]

    if filtered_suggestions:
        print("Search Suggestions:")
        for idx, suggestion in enumerate(filtered_suggestions, start=1):
            print(f"{idx}. {suggestion[0]} --- {suggestion[1]} --- {suggestion[2]}")

        selected_option = input(f"Select a search suggestion (1, 2, 3, ... and {len(filtered_suggestions) + 1} for new search): ")
        if selected_option.isdigit():
            selected_option = int(selected_option)
            if 2 <= selected_option <= len(filtered_suggestions):
                userSearch = filtered_suggestions[selected_option - 1][0]
            elif selected_option == len(filtered_suggestions) + 1:
                userSearch = input("Give the name to get stock price prediction: ")
            elif selected_option == 1:
                print(f"Proceeding with 1st result as search term.")
                userSearch = filtered_suggestions[0][0]
            else:
                print("Invalid option. Proceeding with the original search term.")

    search.clear()
    search.send_keys(userSearch)
    time.sleep(3)
    search.send_keys(Keys.RETURN)

def download_csv(driver, userSearch):
    time.sleep(10)

    hist_data = driver.find_element(By.XPATH, '//li[@data-test="HISTORICAL_DATA"]/a')
    hist_data.click()

    h1_element = driver.find_element(By.XPATH, '//h1[contains(@class, "D(ib) Fz(18px)")]').text

    time.sleep(5)

    download = driver.find_element(By.XPATH, '//span[text()="Download"]')
    download_link = download.find_element(By.XPATH, './..')
    download_link.click()

    time.sleep(15)

    pattern = r'\(([^)]+)\)$'  # Matches text within parentheses
    matches = re.search(pattern, h1_element)

    extracted_text = matches.group(1)

    filename = extracted_text+".csv"

    data = pd.read_csv(".\\CSV Files\\"+filename)

    data['Stock'] = h1_element

    data.to_csv(".\\CSV Files\\"+filename, index=False)

# Main script
if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")  # Removes INFO logging in the terminal
    download_directory = os.path.join(os.getcwd(), "CSV Files")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://finance.yahoo.com")

    while True:
        userSearch = input("Give the name to get stock price prediction (or 'quit' to exit): ")
        if userSearch.lower() == "quit":
            break

        while True:
            get_search_suggestions(driver, userSearch)
            download_csv(driver, userSearch)

            userSearch = input("Enter another search term (or 'quit' to exit this search): ")
            if userSearch.lower() == "quit":
                break

        if userSearch.lower() == "quit":
            break

    driver.quit()

print("Script completed successfully.")
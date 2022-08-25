# finding params for url: "https://www2.daad.de/deutschland/studienangebote/international-programmes/en/result/?q=&degree%5B%5D=2&lang%5B%5D=2&fos=5&cert=&admReq=&langExamPC=&langExamLC=&langExamSC=&langDeAvailable=&langEnAvailable=&lvlEn%5B%5D=&modStd%5B%5D=&cit%5B%5D=&tyi%5B%5D=&ins%5B%5D=&fee=2&bgn%5B%5D=2&dat%5B%5D=&prep_subj%5B%5D=&prep_degree%5B%5D=&sort=4&dur=&subjects%5B%5D=38&limit=10&offset=&display=grid#tab_result-grid"
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import datetime
import pandas as pd
import numpy as np

today = datetime.date.today().isoformat()

logging.basicConfig(filename='./logs/log_'+str(today) +
                    '.txt', level=logging.DEBUG)

parent_url = "https://www2.daad.de/deutschland/studienangebote/international-programmes/en/result/?cert=&admReq=&langExamPC=&langExamLC=&langExamSC=&degree%5B%5D=3&fos=6&langDeAvailable=&langEnAvailable=&lang%5B%5D=2&modStd%5B%5D=&cit%5B%5D=&tyi%5B%5D=&ins%5B%5D=&fee=2&bgn%5B%5D=2&dat%5B%5D=&prep_subj%5B%5D=&prep_degree%5B%5D=&sort=4&dur=&subjects%5B%5D=49&q=&limit=10&offset=&display=list&lvlEn%5B%5D="
driver = webdriver.Chrome(ChromeDriverManager().install())
wait = WebDriverWait(driver, 10)
driver.get(parent_url)

params = ["course", "institution", "url", "admission req",
          "language req", "deadline"]
cols = ["course", "institution", "url", "admission req",
        "language req", "deadline"]

final_data = []


def fetch_links():
    all_urls = []
    # fetch links and go to next page till there is no next button
    try:
        while (True):
            time.sleep(3)
            print("next_available TRUE - going to next page")
            # fetch links and store
            all_urls.extend([item.get_attribute("href") for item in wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".list-inline-item.mr-0.js-course-detail-link")))])
            # click next page if exists
            wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a.js-result-pagination-next"))).click()
    except Exception as e:
        print("next_available FALSE", e)
        pass
        return all_urls


def accept_cookies():
    wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "button.qa-cookie-consent-accept-selected"))).click()


def surf1():
    try:
        # accept cookies
        accept_cookies()

        # fetch links
        all_links = fetch_links()
        return all_links

    except Exception as e:
        print("error occured .... ", e)
        logging.critical(e, exc_info=True)
        pass


def textcombiner(targetIndex):
    all_text = []
    reqs = wait.until(EC.presence_of_all_elements_located((
        By.CSS_SELECTOR, "#registration > .container > .c-description-list > *:nth-child("+targetIndex+") > *")))
    for p in reqs:
        all_text.append(p.get_attribute('innerText'))
        # all_text.append("\n")
    return "\n".join(all_text)


def paramData(param, item_link):
    ["course", "institution", "url", "admission req",
     "language req", "deadline"]
    try:
        if (param == "course"):
            return wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "h2.c-detail-header__title > span:nth-child(1)"))).get_attribute('innerText')
        if (param == "institution"):
            return wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "h3.c-detail-header__subtitle"))).get_attribute('innerHTML').splitlines()[1].strip()
        if (param == "url"):
            return item_link
        if (param == 'admission req'):
            return textcombiner("2")
        if (param == 'language req'):
            return textcombiner("4")
        if (param == 'deadline'):
            return textcombiner("6")
    except Exception as e:
        print('inside exception here: ', e, param)
        logging.critical(e, exc_info=True)


def extractor(item_links):
    if (item_links):
        for item_link in item_links:
            try:
                print("## Visiting Link: ", item_link)
                driver.get(item_link)

                dataFromURL = []

                for param in params:
                    time.sleep(3)
                    dataFromURL.append(paramData(param, item_link))

                print("result: ", dataFromURL)

                final_data.append(dataFromURL)
                # delay before going to next url in the array

                print("Done extracting from: ", item_link)
                time.sleep(3)
            except Exception as e:
                print('inside exception', e)
                logging.critical(e, exc_info=True)
                continue
    if not item_links:
        logging.critical("Empty item_links array.")


def exportCSV():
    # ./Bachelor ./Master ./PHD
    filename = "PHD Informatik Course List for Summer 2023 - Tuition Free"
    df2 = pd.DataFrame(np.array(final_data),
                       columns=cols)
    print(df2)
    df2.to_csv("./PHD/"+filename+".csv", encoding='utf-8-sig')


def main():
    try:
        print("# Starting script ...")
        print("# Visiting parent url: ", parent_url)
        item_links = surf1()
        extractor(item_links)
        exportCSV()
    except Exception as e:
        pass
    finally:
        print('inside finally')
        print("final_data length total: ", len(final_data))
        driver.quit()


if __name__ == "__main__":
    main()

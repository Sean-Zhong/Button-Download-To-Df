from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os, shutil
import time
import pandas as pd

def GetStocks(url='https://www.nasdaq.com/market-activity/stocks/screener',
              selector='body > div.dialog-off-canvas-main-canvas > div > main > div.page__content > article > div:nth-child(3) > div.layout--main > div > div > div.nasdaq-screener__content-container > div:nth-child(2) > div.nasdaq-screener__download > div > button',
              popup=False,
              popup_selector =''):
    temp_folder = 'D:\\temp\stocks_dl'

    # Prevents firefox instance from creating download dialog
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', temp_folder) # custom location
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
  
    # Visits nasdaq.com
    browser = webdriver.Firefox(profile)
    browser.get(url)
    if popup:
        button = browser.find_element_by_css_selector(popup_selector)
        button.click()
        time.sleep(1)

    # Clicks the download button
    button = browser.find_element_by_css_selector(selector)
    button.click()
    time.sleep(3)
    browser.quit()

    # Change filename
    for count, filename in enumerate(os.listdir(temp_folder)):
        dst ="nasdaq" + str(count) + ".csv"
        src = temp_folder + '/' + filename
        dst = temp_folder + '/' + dst
        os.rename(src, dst)

    csv_path = temp_folder + "/nasdaq0.csv"
    df = pd.read_csv(csv_path)

    # Remove files form temp_folder
    for filename in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    return df

# test
if __name__ == '__main__':
    df = GetStocks()
    print(df)
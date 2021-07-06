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

def getSymbols_r(syms, fr=None, src='yahoo'):
    """
    call the R quantmod getSymbols
    """
    import rpy2
    import pandas as pd
    from rpy2.robjects import r
    import rpy2.robjects as ro
    from rpy2.robjects.vectors import StrVector
    from rpy2.robjects.packages import importr
    from rpy2.robjects import Environment, globalenv, pandas2ri
    from rpy2.robjects.conversion import localconverter

    # utils = rpackages.importr('utils')
    # utils.chooseCRANmirror(ind=1)
    ## Install packages
    # packnames = ('quantmod', 'rmgarch')
    # utils.install_packages(StrVector(packnames))

    # Load packages
    # anything require stats.dll need to add current R x64 binaries(C:\Program Files\R\R-4.1.0\bin\x64) in PATH
    #stats = importr('stats')
    #base = importr('base')
    #mgarch = importr('rmgarch')
    #sta = {"skeleton.TA": "skeleton_dot_TA", "skeleton_TA": "skeleton_uscore_TA"}
    #quantmod = importr('quantmod', robject_translations=sta)

    quantmod = importr('quantmod')

    #build the cmd string
    n = len(syms)
    cmd = "getSymbols(c("
    for i in range(n):
        s = syms[i]
        if i < n-1:
            cmd = cmd + '\'' + s + '\','
        else:
            cmd = cmd + '\'' + s + '\'),'
    if not None == fr:
        cmd = cmd + 'fr=\'' + fr + '\','
    cmd = cmd + 'src=\'' + src + '\')'

    df_l = []
	
    # this seems to work for now
    with localconverter(ro.default_converter + pandas2ri.converter):
        # this will return a series of names of xts objects saved in R's globalenv
        names = r(cmd)
        for name in names:
            # convert to df
            c = name + '<-as.data.frame(as.matrix(' + name + '))'
            r(c)
            # retrieve and convert to pandas df
            df = ro.conversion.rpy2py(globalenv[name])
            # the df.index is an unnamed date string series, convert to python date
            df.index = pd.to_datetime(df.index)
            df.index.name = 'Date' # give a name
            df_l.append(df)

    return df_l # can also return pd.concat(df_l, axis=1) as one big df


# test
if __name__ == '__main__':
    df = GetStocks()
    print(df)
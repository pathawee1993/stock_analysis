from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import csv

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--headless")

def writeCsv (filename,data):
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        w = csv.DictWriter(f, data[0].keys())
        w.writeheader()

        # write the data
        for row in data:
            w.writerow(row)

def getTextFromXPATH(driver, xpath):
    text = None
    while text == None:
        text = getElementByXPATH(driver, xpath).text
    return text

def getElementByXPATH (driver, xpath):
    # print(xpath)
    element = None
    while (element == None):
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, xpath))
        )
    
    return driver.find_element(By.XPATH,xpath)
    # return element

def getStockData (driver, name, wkn, link):
    stockData = []
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options=chrome_options)
    driver.get(link)
    time.sleep(5)

    land = getTextFromXPATH(driver, "/html/body/app-root/app-wrapper/div/div[2]/app-equity/div[2]/div[5]/div[1]/app-widget-equity-master-data/div/div/table/tbody/tr[5]/td[2]")
    branche = getTextFromXPATH(driver, "/html/body/app-root/app-wrapper/div/div[2]/app-equity/div[2]/div[5]/div[1]/app-widget-equity-master-data/div/div/table/tbody/tr[6]/td[2]")
    
    driver.get(link+'/kennzahlen')

    _len = 1
    while _len == 1:
        head = getElementByXPATH(driver, "/html/body/app-root/app-wrapper/div/div[2]/app-equity/div[2]/div[3]/app-widget-historical-key-data/div/div/div/div/table/thead")
        _len = len(head.find_elements(By.TAG_NAME, "th"))
    print(name, wkn, land, branche,_len)
    baseXpath = "/html/body/app-root/app-wrapper/div/div[2]/app-equity/div[2]/div[3]/app-widget-historical-key-data/div/div/div/div/table/tbody"
    for i in range(2, _len):
        stockData.append({
            "name": name,
            "wkn": wkn,
            "land": land,
            "branche": branche,
            "year": getTextFromXPATH(driver, "/html/body/app-root/app-wrapper/div/div[2]/app-equity/div[2]/div[3]/app-widget-historical-key-data/div/div/div/div/table/thead/tr/th["+str(i)+"]"),
            "waehrung": getTextFromXPATH(driver,baseXpath+"/tr[1]/td["+str(i)+"]"),
            "start_kurse": 0,
            "end_kurse": 0,
            "umsatz": getTextFromXPATH(driver,baseXpath+"/tr[2]/td["+str(i)+"]"),
            "ebit": getTextFromXPATH(driver,baseXpath+"/tr[4]/td["+str(i)+"]"),
            "ebt": getTextFromXPATH(driver,baseXpath+"/tr[5]/td["+str(i)+"]"),
            "ergebnis_je_aktie": getTextFromXPATH(driver,baseXpath+"/tr[22]/td["+str(i)+"]"),
            "dividend_je_aktie": getTextFromXPATH(driver,baseXpath+"/tr[23]/td["+str(i)+"]"),
            "umsatz_je_aktie": getTextFromXPATH(driver,baseXpath+"/tr[26]/td["+str(i)+"]"),
            "buchwert_je_aktie": getTextFromXPATH(driver,baseXpath+"/tr[27]/td["+str(i)+"]"),
            "cashflow_je_aktie": getTextFromXPATH(driver,baseXpath+"/tr[28]/td["+str(i)+"]"),
            "bilanzsumme_je_Aktie": getTextFromXPATH(driver,baseXpath+"/tr[29]/td["+str(i)+"]"),
            "kgv": getTextFromXPATH(driver,baseXpath+"/tr[30]/td["+str(i)+"]"),
            "kbv": getTextFromXPATH(driver,baseXpath+"/tr[31]/td["+str(i)+"]"),
            "kuv": getTextFromXPATH(driver,baseXpath+"/tr[32]/td["+str(i)+"]"),
            "kcv": getTextFromXPATH(driver,baseXpath+"/tr[33]/td["+str(i)+"]"),
            "dividendenrendite": getTextFromXPATH(driver,baseXpath+"/tr[34]/td["+str(i)+"]"),
            "gewinnrendite": getTextFromXPATH(driver,baseXpath+"/tr[35]/td["+str(i)+"]"),
            "eigenkapitalrendite": getTextFromXPATH(driver,baseXpath+"/tr[36]/td["+str(i)+"]"),
            "umsatzrendite": getTextFromXPATH(driver,baseXpath+"/tr[37]/td["+str(i)+"]"),
            "gesamtkapitalrendite": getTextFromXPATH(driver,baseXpath+"/tr[38]/td["+str(i)+"]"),
            "roi": getTextFromXPATH(driver,baseXpath+"/tr[39]/td["+str(i)+"]"),
            "arbeitsintensität": getTextFromXPATH(driver,baseXpath+"/tr[40]/td["+str(i)+"]"),
            "eigenkapitalquote": getTextFromXPATH(driver,baseXpath+"/tr[41]/td["+str(i)+"]"),
            "fremdkapitalquote": getTextFromXPATH(driver,baseXpath+"/tr[42]/td["+str(i)+"]"),
            "verschuldungsgrad": getTextFromXPATH(driver,baseXpath+"/tr[43]/td["+str(i)+"]"),
            "anzahl_mitarbeiter": getTextFromXPATH(driver,baseXpath+"/tr[45]/td["+str(i)+"]"),
            "umsatz_je_mitarbeiter": getTextFromXPATH(driver,baseXpath+"/tr[47]/td["+str(i)+"]"),
            "bruttoergebnis_je_mitarbeiter": getTextFromXPATH(driver,baseXpath+"/tr[49]/td["+str(i)+"]"),
            "gewinn_je_mitarbeiter": getTextFromXPATH(driver,baseXpath+"/tr[50]/td["+str(i)+"]"),
        })

    # print(stockData)
    # driver.close()
    return stockData

def getAllStock ():


    stocks = []
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options=chrome_options)
    driver.get('https://www.boerse-frankfurt.de/aktien/suche')

    driver2 = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options=chrome_options)

    i = 0
    while True:
        table = getElementByXPATH(driver, '/html/body/app-root/app-wrapper/div/div[2]/app-equity-search/app-equity-search-result-table/div/div[2]/table/tbody')
        rows = table.find_elements(By.TAG_NAME, "tr") # get all of the rows in the table
        for row in rows:
            start_time = time.time()
            col1 = row.find_elements(By.TAG_NAME, "td")[0] #note: index start from 0, 1 is col 2  
            name = col1.text
            a = col1.find_elements(By.TAG_NAME, "a")[0]
            url = a.get_attribute("href")
            wkn = row.find_elements(By.TAG_NAME, "td")[1].text #note: index start from 0, 1 is col 2
            stockData = getStockData(driver2, name, wkn, url)
            stocks = stocks+stockData
            print("--- %s seconds ---" % (time.time() - start_time))


        nextBtn=driver.find_element(By.XPATH,"/html/body/app-root/app-wrapper/div/div[2]/app-equity-search/app-equity-search-result-table/div/app-page-bar[1]/div/div[1]/button[9]")
        if (nextBtn is None or i == 0):
            break
        
        nextBtn.click()
        i = i +1
    writeCsv('stock.csv', stocks)


def main ():
    stock = getAllStock()
    print(stock)

main()
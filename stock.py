from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import csv
import psycopg2
from database_config import config

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

def getNumFromXPATH(driver, xpath):
    text = None
    while text == None:
        text = getElementByXPATH(driver, xpath).text
    return getNum(text)

def getElementByXPATH (driver, xpath):
    # print(xpath)
    element = None
    while (element == None):
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, xpath))
        )
    
    return driver.find_element(By.XPATH,xpath)
    # return element

def getNum (strNum):
    try:
        strNum = strNum.replace(".","")
        strNum = strNum.replace(",",".")
        return float(strNum)
    except:
        return 'null'



def toDatabase (aktienDaten):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        values = ""
        for r in aktienDaten:
            # print(r)
            values = values + f"('{r['name']}','{r['wkn']}','{r['land']}','{r['branche']}',{r['year']},'{r['waehrung']}',{r['kurse']}, {r['umsatz']},{r['ebit']}, {r['ebt']}, {r['ergebnis_je_aktie']}, {r['dividend_je_aktie']}, {r['umsatz_je_aktie']}, {r['buchwert_je_aktie']}, {r['cashflow_je_aktie']}, {r['bilanzsumme_je_aktie']}, {r['kgv']}, {r['kbv']}, {r['kuv']}, {r['kcv']}, {r['dividendenrendite']}, {r['gewinnrendite']}, {r['eigenkapitalrendite']}, {r['umsatzrendite']}, {r['gesamtkapitalrendite']}, {r['roi']}, {r['arbeitsintensitaet']}, {r['eigenkapitalquote']}, {r['fremdkapitalquote']}, {r['verschuldungsgrad']}, {r['anzahl_mitarbeiter']}, {r['umsatz_je_mitarbeiter']}, {r['bruttoergebnis_je_mitarbeiter']}, {r['gewinn_je_mitarbeiter']}),\n"
        # create a cursor
        cur = conn.cursor()
        
	    # execute a statement
        cmd = f"""INSERT INTO public.aktien_daten
            ("name", wkn, land, branche, "year", waehrung, kurse, umsatz, ebit, ebt, ergebnis_je_aktie, dividend_je_aktie, umsatz_je_aktie, buchwert_je_aktie, cashflow_je_aktie, bilanzsumme_je_aktie, kgv, kbv, kuv, kcv, dividendenrendite, gewinnrendite, eigenkapitalrendite, umsatzrendite, gesamtkapitalrendite, roi, arbeitsintensitaet, eigenkapitalquote, fremdkapitalquote, verschuldungsgrad, anzahl_mitarbeiter, umsatz_je_mitarbeiter, bruttoergebnis_je_mitarbeiter, gewinn_je_mitarbeiter)
            VALUES{values[:-2]};"""
        # print(cmd)
        cur.execute(cmd)

        # display the PostgreSQL database server version
        conn.commit()
       
	    # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def updateAktienDaten (driver, name, wkn, link):
    aktienDaten = []
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
    for i in range(2, _len+1):
        try:
            ergebnis_je_aktie = getNumFromXPATH(driver,baseXpath+"/tr[22]/td["+str(i)+"]")
            kgv = getNumFromXPATH(driver,baseXpath+"/tr[30]/td["+str(i)+"]")
            kurse = round(kgv*ergebnis_je_aktie, 2)
            if (kurse > 0):
                aktienDaten.append({
                    "name": name,
                    "wkn": wkn,
                    "land": land,
                    "branche": branche,
                    "year": getNumFromXPATH(driver, "/html/body/app-root/app-wrapper/div/div[2]/app-equity/div[2]/div[3]/app-widget-historical-key-data/div/div/div/div/table/thead/tr/th["+str(i)+"]"),
                    "waehrung": getTextFromXPATH(driver,baseXpath+"/tr[1]/td["+str(i)+"]"),
                    "kurse": kurse,
                    "umsatz": getNumFromXPATH(driver,baseXpath+"/tr[2]/td["+str(i)+"]"),
                    "ebit": getNumFromXPATH(driver,baseXpath+"/tr[4]/td["+str(i)+"]"),
                    "ebt": getNumFromXPATH(driver,baseXpath+"/tr[5]/td["+str(i)+"]"),
                    "ergebnis_je_aktie": ergebnis_je_aktie,
                    "dividend_je_aktie": getNumFromXPATH(driver,baseXpath+"/tr[23]/td["+str(i)+"]"),
                    "umsatz_je_aktie": getNumFromXPATH(driver,baseXpath+"/tr[26]/td["+str(i)+"]"),
                    "buchwert_je_aktie": getNumFromXPATH(driver,baseXpath+"/tr[27]/td["+str(i)+"]"),
                    "cashflow_je_aktie": getNumFromXPATH(driver,baseXpath+"/tr[28]/td["+str(i)+"]"),
                    "bilanzsumme_je_aktie": getNumFromXPATH(driver,baseXpath+"/tr[29]/td["+str(i)+"]"),
                    "kgv": kgv,
                    "kbv": getNumFromXPATH(driver,baseXpath+"/tr[31]/td["+str(i)+"]"),
                    "kuv": getNumFromXPATH(driver,baseXpath+"/tr[32]/td["+str(i)+"]"),
                    "kcv": getNumFromXPATH(driver,baseXpath+"/tr[33]/td["+str(i)+"]"),
                    "dividendenrendite": getNumFromXPATH(driver,baseXpath+"/tr[34]/td["+str(i)+"]"),
                    "gewinnrendite": getNumFromXPATH(driver,baseXpath+"/tr[35]/td["+str(i)+"]"),
                    "eigenkapitalrendite": getNumFromXPATH(driver,baseXpath+"/tr[36]/td["+str(i)+"]"),
                    "umsatzrendite": getNumFromXPATH(driver,baseXpath+"/tr[37]/td["+str(i)+"]"),
                    "gesamtkapitalrendite": getNumFromXPATH(driver,baseXpath+"/tr[38]/td["+str(i)+"]"),
                    "roi": getNumFromXPATH(driver,baseXpath+"/tr[39]/td["+str(i)+"]"),
                    "arbeitsintensitaet": getNumFromXPATH(driver,baseXpath+"/tr[40]/td["+str(i)+"]"),
                    "eigenkapitalquote": getNumFromXPATH(driver,baseXpath+"/tr[41]/td["+str(i)+"]"),
                    "fremdkapitalquote": getNumFromXPATH(driver,baseXpath+"/tr[42]/td["+str(i)+"]"),
                    "verschuldungsgrad": getNumFromXPATH(driver,baseXpath+"/tr[43]/td["+str(i)+"]"),
                    "anzahl_mitarbeiter": getNumFromXPATH(driver,baseXpath+"/tr[45]/td["+str(i)+"]"),
                    "umsatz_je_mitarbeiter": getNumFromXPATH(driver,baseXpath+"/tr[47]/td["+str(i)+"]"),
                    "bruttoergebnis_je_mitarbeiter": getNumFromXPATH(driver,baseXpath+"/tr[49]/td["+str(i)+"]"),
                    "gewinn_je_mitarbeiter": getNumFromXPATH(driver,baseXpath+"/tr[50]/td["+str(i)+"]"),
                })
        except:
            print("An exception occurred")

    print(aktienDaten)
    # driver.close()
    toDatabase(aktienDaten)

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
            updateAktienDaten(driver2, name, wkn, url)
            print("--- %s seconds ---" % (time.time() - start_time))


        nextBtn=driver.find_element(By.XPATH,"/html/body/app-root/app-wrapper/div/div[2]/app-equity-search/app-equity-search-result-table/div/app-page-bar[1]/div/div[1]/button[9]")
        if (nextBtn is None or i == 0):
            break
        
        nextBtn.click()
        i = i +1
    # writeCsv('stock.csv', stocks)


def main ():
    getAllStock()

main()

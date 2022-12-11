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
from config.database_config import config
import sys

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
        # print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        values = ""
        for r in aktienDaten:
            # print(r)
            values = values + f"('{r['name']}','{r['wkn']}','{r['land']}','{r['branche']}',{r['year']},'{r['waehrung']}',{r['kurse']}, {r['umsatz']},{r['ebit']}, {r['ebt']}, {r['ergebnis_n_steuer']}, {r['eigenkapital']}, {r['gesamtkapital']}, {r['ergebnis_je_aktie']}, {r['dividend_je_aktie']}, {r['umsatz_je_aktie']}, {r['buchwert_je_aktie']}, {r['cashflow_je_aktie']}, {r['bilanzsumme_je_aktie']}, {r['kgv']}, {r['kbv']}, {r['kuv']}, {r['kcv']}, {r['dividendenrendite']}, {r['gewinnrendite']}, {r['eigenkapitalrendite']}, {r['umsatzrendite']}, {r['roi']}),\n"
        # create a cursor
        cur = conn.cursor()
        
	    # execute a statement
        cmd = f"""INSERT INTO public.aktien_daten
            ("name", wkn, land, branche, "year", waehrung, kurse, umsatz, ebit, ebt, ergebnis_n_steuer, eigenkapital, gesamtkapital, ergebnis_je_aktie, dividend_je_aktie, umsatz_je_aktie, buchwert_je_aktie, cashflow_je_aktie, bilanzsumme_je_aktie, kgv, kuv, kbv, kcv, dividendenrendite, gewinnrendite, eigenkapitalrendite, umsatzrendite, roi)
            VALUES{values[:-2]} 
            on conflict (wkn, year)
            do update set kurse = EXCLUDED.kurse,umsatz = EXCLUDED.umsatz,ebit = EXCLUDED.ebit,ebt = EXCLUDED.ebt,ergebnis_n_steuer = EXCLUDED.ergebnis_n_steuer,eigenkapital = EXCLUDED.eigenkapital,gesamtkapital = EXCLUDED.gesamtkapital,ergebnis_je_aktie = EXCLUDED.ergebnis_je_aktie,dividend_je_aktie = EXCLUDED.dividend_je_aktie,umsatz_je_aktie = EXCLUDED.umsatz_je_aktie,
            buchwert_je_aktie = EXCLUDED.buchwert_je_aktie,cashflow_je_aktie = EXCLUDED.cashflow_je_aktie,bilanzsumme_je_aktie = EXCLUDED.bilanzsumme_je_aktie,kgv = EXCLUDED.kgv,kuv = EXCLUDED.kuv,kbv = EXCLUDED.kbv,kcv = EXCLUDED.kcv,dividendenrendite = EXCLUDED.dividendenrendite,gewinnrendite = EXCLUDED.gewinnrendite,
            eigenkapitalrendite = excluded.eigenkapitalrendite, umsatzrendite = excluded.umsatzrendite, roi = excluded.roi
            ;"""
            # arbeitsintensitaet = excluded.arbeitsintensitaet, eigenkapitalquote = excluded.eigenkapitalquote, fremdkapitalquote = excluded.fremdkapitalquote, verschuldungsgrad = excluded.verschuldungsgrad, anzahl_mitarbeiter=excluded.anzahl_mitarbeiter, umsatz_je_mitarbeiter=excluded.umsatz_je_mitarbeiter, bruttoergebnis_je_mitarbeiter=excluded.bruttoergebnis_je_mitarbeiter, gewinn_je_mitarbeiter=excluded.gewinn_je_mitarbeiter
        # print(cmd)

        cur.execute(cmd)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            # print('Database connection closed.')

def updateAktienDaten (driver, name, wkn, link):
    aktienDaten = []
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options=chrome_options)
    driver.get(link)
    time.sleep(5)

    land = getTextFromXPATH(driver, "/html/body/app-root/app-wrapper/div/div[2]/app-equity/div[2]/div[5]/div[1]/app-widget-equity-master-data/div/div/table/tbody/tr[5]/td[2]")
    branche = getTextFromXPATH(driver, "/html/body/app-root/app-wrapper/div/div[2]/app-equity/div[2]/div[5]/div[1]/app-widget-equity-master-data/div/div/table/tbody/tr[6]/td[2]")
    
    driver.get(link+'/kennzahlen')
    time.sleep(5)

    _len = 1
    cout = 0
    while _len == 1:
        head = getElementByXPATH(driver, "/html/body/app-root/app-wrapper/div/div[2]/app-equity/div[2]/div[3]/app-widget-historical-key-data/div/div/div/div/table/thead")
        _len = len(head.find_elements(By.TAG_NAME, "th"))
        cout = cout + 1
        if (cout == 3):
            return
    print(name, wkn, land, branche,_len)
    baseXpath = "/html/body/app-root/app-wrapper/div/div[2]/app-equity/div[2]/div[3]/app-widget-historical-key-data/div/div/div/div/table/tbody"
    for i in range(2, _len+1):
        try:
            umsatz = getNumFromXPATH(driver,baseXpath+"/tr[2]/td["+str(i)+"]")
            umsatz_je_aktie = getNumFromXPATH(driver,baseXpath+"/tr[26]/td["+str(i)+"]")
            if (umsatz_je_aktie == 0):
                umsatz_je_aktie = umsatz/getNumFromXPATH(driver,baseXpath+"/tr[18]/td["+str(i)+"]")
            ergebnis_je_aktie = getNumFromXPATH(driver,baseXpath+"/tr[22]/td["+str(i)+"]")
            dividend_je_aktie = getNumFromXPATH(driver,baseXpath+"/tr[23]/td["+str(i)+"]")
            dividend_je_aktie = dividend_je_aktie if (dividend_je_aktie != 'null') else 0 # revise value
            buchwert_je_aktie = getNumFromXPATH(driver,baseXpath+"/tr[27]/td["+str(i)+"]")
            cashflow_je_aktie = getNumFromXPATH(driver,baseXpath+"/tr[28]/td["+str(i)+"]")
            kuv = getNumFromXPATH(driver,baseXpath+"/tr[31]/td["+str(i)+"]")
            kbv = getNumFromXPATH(driver,baseXpath+"/tr[31]/td["+str(i)+"]")
            kcv = getNumFromXPATH(driver,baseXpath+"/tr[31]/td["+str(i)+"]")
            kurse = 0
            if (kuv != 'null' and umsatz_je_aktie != 'null' and umsatz_je_aktie != 0):
                kurse = round(kuv*umsatz_je_aktie, 2)
            elif (kbv != 'null' and buchwert_je_aktie != 'null' and buchwert_je_aktie != 0):
                kurse = round(kbv*buchwert_je_aktie, 2)
            elif (kcv != 'null' and cashflow_je_aktie != 'null' and cashflow_je_aktie != 0):
                kurse = round(kcv*cashflow_je_aktie, 2)
            else:
                continue # if cannot get kurse -> go to next year
            kgv = round(kurse/ergebnis_je_aktie, 2)
            kbv = round(kurse/buchwert_je_aktie, 2)
            kcv = round(kurse/cashflow_je_aktie, 2)
            ergebnis_n_steuer = getNumFromXPATH(driver,baseXpath+"/tr[7]/td["+str(i)+"]")
            eigenkapital = getNumFromXPATH(driver,baseXpath+"/tr[16]/td["+str(i)+"]")
            gesamtkapital = getNumFromXPATH(driver,baseXpath+"/tr[17]/td["+str(i)+"]")
            eigenkapital = eigenkapital if (eigenkapital != 'null') else gesamtkapital - getNumFromXPATH(driver,baseXpath+"/tr[15]/td["+str(i)+"]") # revise value

            if (kurse > 0):
                aktienDaten.append({
                    "name": name,
                    "wkn": wkn,
                    "land": land,
                    "branche": branche,
                    "year": getNumFromXPATH(driver, "/html/body/app-root/app-wrapper/div/div[2]/app-equity/div[2]/div[3]/app-widget-historical-key-data/div/div/div/div/table/thead/tr/th["+str(i)+"]"),
                    "waehrung": getTextFromXPATH(driver,baseXpath+"/tr[1]/td["+str(i)+"]"),
                    "kurse": kurse,
                    "umsatz": umsatz,
                    "ebit": getNumFromXPATH(driver,baseXpath+"/tr[4]/td["+str(i)+"]"),
                    "ebt": getNumFromXPATH(driver,baseXpath+"/tr[5]/td["+str(i)+"]"),
                    "ergebnis_n_steuer": ergebnis_n_steuer,
                    "eigenkapital": eigenkapital,
                    "gesamtkapital": gesamtkapital,
                    "ergebnis_je_aktie": ergebnis_je_aktie,
                    "dividend_je_aktie": dividend_je_aktie,
                    "umsatz_je_aktie": umsatz_je_aktie,
                    "buchwert_je_aktie": buchwert_je_aktie,
                    "cashflow_je_aktie": cashflow_je_aktie,
                    "bilanzsumme_je_aktie": getNumFromXPATH(driver,baseXpath+"/tr[29]/td["+str(i)+"]"),
                    "kgv": kgv,
                    "kuv": kuv,
                    "kbv": kbv,
                    "kcv": kcv,
                    "dividendenrendite": round((dividend_je_aktie/kurse)*100,2),
                    "gewinnrendite": round((1/kgv)*100,2),
                    "eigenkapitalrendite": round((ergebnis_n_steuer/eigenkapital)*100,2),
                    "umsatzrendite": round(ergebnis_je_aktie/umsatz_je_aktie*100,2),
                    "roi": round((ergebnis_n_steuer/gesamtkapital)*100,2)
                })
        except Exception as e: print(e)

    # print(aktienDaten)
    # driver.close()
    toDatabase(aktienDaten)

def getAllStock ():

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options=chrome_options)
    driver.get('https://www.boerse-frankfurt.de/aktien/suche?MARKET_CAPITALISATION_MIN=10000000&ORDER_BY=TURNOVER&ORDER_DIRECTION=DESC')
    time.sleep(10)

    driver2 = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options=chrome_options)

    page = int(sys.argv[1])
    i = 1
    while True:
        print("page >",i)
        table = getElementByXPATH(driver, '/html/body/app-root/app-wrapper/div/div[2]/app-equity-search/app-equity-search-result-table/div/div[2]/table/tbody')
        rows = table.find_elements(By.TAG_NAME, "tr") # get all of the rows in the table
        if (i >= page):
            for row in rows:
                try:
                    start_time = time.time()
                    col1 = row.find_elements(By.TAG_NAME, "td")[0] #note: index start from 0, 1 is col 2  
                    name = col1.text
                    a = col1.find_elements(By.TAG_NAME, "a")[0]
                    url = a.get_attribute("href")
                    wkn = row.find_elements(By.TAG_NAME, "td")[1].text #note: index start from 0, 1 is col 2
                    updateAktienDaten(driver2, name, wkn, url)
                    print("--- %s seconds ---" % (time.time() - start_time))
                except Exception as e: print(e)

        newtable = getElementByXPATH(driver, '/html/body/app-root/app-wrapper/div/div[2]/app-equity-search/app-equity-search-result-table/div/div[2]/table/tbody')
        newrows = newtable.find_elements(By.TAG_NAME, "tr") # get all of the rows in the table
        while (rows[0] == newrows[0]):
            tabs=getElementByXPATH(driver,"/html/body/app-root/app-wrapper/div/div[2]/app-equity-search/app-equity-search-result-table/div/app-page-bar[1]/div/div[1]")
            btns = tabs.find_elements(By.TAG_NAME, "button")
            nextBtn = btns[len(btns)-2]
            if (nextBtn is None):
                break
            
            nextBtn.click()
            time.sleep(20)
            newtable = getElementByXPATH(driver, '/html/body/app-root/app-wrapper/div/div[2]/app-equity-search/app-equity-search-result-table/div/div[2]/table/tbody')
            newrows = table.find_elements(By.TAG_NAME, "tr") # get all of the rows in the table
        i = i +1
    # writeCsv('stock.csv', stocks)


def main ():
    getAllStock()

main()


import requests
from bs4 import BeautifulSoup
import math
import pandas as pd
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from data.credentials import USERNAME, PASSWORD

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
logging.getLogger('').addHandler(console)

l = []
o = {}
k = []
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/107.0.0.0 Safari/537.36"}

driver = webdriver.Chrome()
driver.get('https://www.linkedin.com/')

username_field = driver.find_element(By.ID, 'session_key')
password_field = driver.find_element(By.ID, 'session_password')
submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
username_field.send_keys(USERNAME)
password_field.send_keys(PASSWORD)
submit_button.click()

logging.info("Accesso completato. Inizio l'estrazione dei dati dai lavori LinkedIn")

WebDriverWait(driver, 10).until(EC.url_matches("https://www.linkedin.com/feed/"))

target_url = 'https://www.linkedin.com/jobs/search/?currentJobId=3811034222&distance=25&geoId=103350119&keywords=data' \
             '%20analyst&origin=JOBS_HOME_KEYWORD_HISTORY&refresh=true '
for i in range(0, math.ceil(117 / 25)):

    res = requests.get(target_url.format(i))
    soup = BeautifulSoup(res.text, 'html.parser')
    alljobs_on_this_page = soup.find_all("li")
    for x in range(0, len(alljobs_on_this_page)):
        base_card = alljobs_on_this_page[x].find("div", {"class": "base-card"})
        if base_card:
            jobid = base_card.get('data-entity-urn').split(":")[3]
            l.append(jobid)
            logging.info(f"Pagina {i + 1}: {len(alljobs_on_this_page)} lavori trovati")

target_url = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}'
for j in range(0, len(l)):

    resp = requests.get(target_url.format(l[j]))
    soup = BeautifulSoup(resp.text, 'html.parser')

    try:
        o["company"] = soup.find("div", {"class": "top-card-layout__card"}).find("a").find("img").get('alt')
    except:
        o["company"] = None

    try:
        o["job-title"] = soup.find("div", {"class": "top-card-layout__entity-info"}).find("a").text.strip()
    except:
        o["job-title"] = None

    try:
        o["level"] = soup.find("ul", {"class": "description__job-criteria-list"}).find("li").text.replace(
            "Seniority level", "").strip()
    except:
        o["level"] = None

    logging.info(f"Lavoro {j + 1}/{len(l)} elaborato")

    k.append(o)
    o = {}

df = pd.DataFrame(k, columns=["company", "job-title", "level"])
df.to_csv('linkedinjobs.csv', index=False, encoding='utf-8')
# print(k)
logging.info("CSV creato con successo")

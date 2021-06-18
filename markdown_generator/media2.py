import sys
import time
import json
from bs4 import BeautifulSoup
import frontmatter
import pandas as pd
import os
from newsfetch.news import newspaper
from tqdm import tqdm
from pprint import pprint
from newspaper import Article
import waybackpy
import requests
import random
import datetime
import article_parser

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


try:
    implicit_wait = 10
    if 'win' in sys.platform:
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(implicit_wait)  # seconds
    else:
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(implicit_wait)  # seconds


    dirs = [x[0].split("/")[-1] for x in os.walk("../content/media")]
    dirs = [x for x in dirs if x != "media"]
    # random.shuffle(dirs)

    already_complete = []
    out = []
    with open("media2.jsonl", "r") as f:
        for line in f:
            j = json.loads(line)
            if 'outline_html' in j:
                already_complete.append(j['external_link'])
                out.append(j)

    print(f"ALREADY COMPLETE: {len(already_complete)}")

    with open("media2.jsonl", "a") as f:
        for dir in tqdm(dirs):
            fn = "../content/media/{}/index.md".format(dir)
            post = frontmatter.load(fn)
            res = post.to_dict()

            if 'external_link' in res:
                try:

                    if 'web.archive.org' in res['external_link']:
                        res['external_link'] = 'http' + res['external_link'].split('http')[-1]

                    print(res['external_link'])
                    
                    if "health.usnews.com" in res['external_link']:
                        continue

                    if "newsmax.com" in res['external_link']:
                        continue

                    if res['external_link'] in already_complete:
                        continue

                    ## Print Time
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    ## Check site
                    print("CHECK SITE")
                    try:
                        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
                        r = requests.get(res['external_link'], verify = False, headers = headers)
                        if r.status_code != 200:
                            print(f"REQUESTS ERROR: {r.status_code}")
                            continue
                    except:
                        pass
                        # continue

                    ## Outline.com
                    print("OUTLINE.COM")
                    try:

                        # title, content = article_parser.parse(res['external_link'])
                        # res['article_parser_content'] = content.replace("\n", "<br><br>")
                        # print(res['article_parser_content'])
                        driver.get(f"https://www.outline.com/{res['external_link']}")
                        # linkbar = driver.find_element_by_id('source')
                        # linkbar.send_keys(res['external_link'])
                        # driver.save_screenshot("URL.png")
                        # linkbar.send_keys(Keys.ENTER)
                        # driver.save_screenshot("ENTER.png")
                        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "raw")))
                        driver.save_screenshot("WAITING.png")
                        time.sleep(3)
                        driver.save_screenshot("DONE.png")
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        raw = soup.select('raw[content]')
                        if len(raw) > 0:
                            html = str(raw[0]['content'])
                            res['outline_html'] = html
                        att = soup.find_all('img', {'class': 'logo'})
                        if len(att) > 0:
                            img = str(att[0]['src'])
                            res['outline_img'] = img

                    except Exception as e:
                        print(f"OUTLINE ERROR: {str(e)}")
                        # print(driver.save_screenshot("ERROR.png"))
                        pass

                    # Wayback Machine
                    print("WAYBACK MACHINE")
                    wayback = waybackpy.Url(res['external_link'])
                    try:
                        res['archived_url'] = wayback.newest().archive_url
                    except:
                        print("SAVING ON WAYBACK")
                        wayback.save()
                        res['archived_url'] = wayback.newest().archive_url

                    # Newspape Metadata
                    print("NEWSFETCH")
                    n = newspaper(res['external_link']).get_dict
                    res['headline']     = n['headline']
                    res['summary']      = n['summary']
                    res['article']      = n['article']
                    res['description']  = n['description']
                    res['publication']  = n['publication']
                    res['date']         = n['date_publish']
                    res['url']          = n['url']
                    res['original_url'] = n['url']

                    f.write(json.dumps(res))
                    f.write("\n")
                    f.flush()

                    out.append(res)

                except Exception as e:
                    print(f"OVERALL ERROR: {str(e)}")
                    pass

                time.sleep(3 * (1 + random.random()))

    df = pd.DataFrame(out)
    print(df.head())
    print(df.tail())
    df.to_csv("media.csv", encoding="utf8", index = False)

finally:
    driver.close()
    driver.quit()


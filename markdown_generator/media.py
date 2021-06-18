from newsfetch.news import newspaper
import frontmatter
import os
import requests
from tqdm import tqdm
import json
from pprint import pprint
import random
import datetime
import time
import justext
from fake_useragent import UserAgent
import random
ua = UserAgent()

# >> > 
# >> > s.extract()
# >> > s.title
# u'svven/summary'
# >> > s.image
# https: // avatars0.githubusercontent.com / u / 7524085?s = 400
# >> > s.description


dirs = [x[0].split("/")[-1] for x in os.walk("../content/media")]
dirs = [x for x in dirs if x != "media"]
dirs = sorted(dirs)

# random.shuffle(dirs)

def get_frontmatter(fn):
    post = frontmatter.load(fn)
    return post.to_dict()

# dirs = [
#     "gma",
#     "medical_research",
#     "medpage",
#     "msn",
#     "news2"
# ]

# with open("missing.txt", "r") as f:
#     missing = f.readlines()
#     missing = [x.replace("\n", "") for x in missing]

# dirs = [x for x in dirs if x not in missing]
# random.shuffle(dirs)

def get_outline(url):
    u = ua.random
    headers = {
        # 'authority': 'www.google.com',
        # 'sec-ch-ua': '^\\^',
        # 'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        # 'sec-ch-ua-mobile': '?0',
        # 'origin': 'https://outline.com',
        # 'sec-fetch-site': 'cross-site',
        # 'sec-fetch-mode': 'no-cors',
        # 'sec-fetch-dest': 'image',
        # 'referer': 'https://outline.com/',
        # 'accept-language': 'en-US,en;q=0.9',
        # 'cookie': '__Secure-3PSID=-gfRMYlxpJ5Yzwol2HYPFy_l-IuUEtuHZglxgLFdutQVyoOzus6jUaAmAhIjSLZFbb8o4A.; __Secure-3PAPISID=0c8-gcRtKJme6a5p/AFo5G1QawYgPC_pZ0; NID=217=GbpY7JMnzA5VwmxYySKx4ECH_hi5ImvInaGx0rqQgRWeciwNFe8L-7qJTNx1HyNRO71Sf1NhJTOu6qHKPCgqNnWDyCnUyhIPxb0hxSOjF9iuRLvVlXXzewM-GDz8GFoTFvi7npRtTF4L_tjMP6Xkno2b9VyLw1MVy4N2xyBQN7n3CJM4FSGJ7-6oE4a0SVvb9aQs1AmjyggHxANDOH44UJTX3uKHCsF5T6Pp1LxFVOvSXC4iVSIrR5HwK0xpE1GYKSUHALuyLUrlPwmFz1zVBvqzCvISGzzGFkLEknF_vMgRmPjq6N76aChLUob4wDXA2XA33LwMx8D7uO3NjIM; 1P_JAR=2021-06-16-19; __Secure-3PSIDCC=AJi4QfF8mymEV0OP0tXNoGcwJMS14NKfq0hHkjDIN-eRZW9L_B90wNAAwUqpCXjLTkbRI8cdqr8E',
        # 'x-client-data': 'CJK2yQEIprbJAQjBtskBCKmdygEI0qDKAQigoMsBCMCgywEI3PLLAQi0+MsB',
        # 'Referer': 'https://outline.com/css/outline.css?v=1.0.1',
        # 'Origin': 'https://outline.com',
        'user-agent': u,
        'User-Agent': u,
    }

    # pprint(headers)
    params = (
        ('source_url', url),
    )

    # pprint(params)
    response = requests.get('https://api.outline.com/v3/parse_article', headers=headers, params=params)
    # pprint(response)

    if response.status_code == 429:
        print(f"PROBLEM [{response.status_code}]: {url}")
        pprint(response.json())

    if response.status_code != 200:
        print(f"PROBLEM [{response.status_code}]: {url}")
        # pprint(r.__dict__)
        return None

    j = response.json()
    if 'data' in j:
        if 'html' in j['data']:
            return j['data']['html']
    return None


sl = justext.get_stoplist("English")
r = requests.Session()
def get_outline2(url, sl = sl, r = r):
    try:
        timeout_secs = 10
        u = ua.random
        r.headers = {'user-agent': u}
        page = r.get(url, verify=True, timeout=timeout_secs)
        paragraphs = justext.justext(page.content, sl)
        text = "<br><br>".join([x.text for x in paragraphs if not x.is_boilerplate or len(x.text.split()) > 5])
        return text
    except Exception as e:
        print(f"OUTLINE ERROR {str(e)}")
        return None


with open("media.jsonl", "a") as f, open("missing.txt", "a") as f2:
    for dir in tqdm(dirs):
        try:

            fn = "../content/media/{}/index.md".format(dir)
            with open(fn, "r") as f4:
                if f4.read() == "":
                    with open("blank.txt", "a") as f5:
                        f5.write(dir)
                        f5.write("\n")
                    continue

            # print("CP1")
            post = frontmatter.load(fn)
            out = post.to_dict()
            # print("CP2")

            # out = get_frontmatter(fn)
            out['dir'] = dir

            # print("CP3")
            if 'external_link' in out:
                external_link = out['external_link']
                post['original_lnk'] = external_link
                del post['external_link']
            else:
                external_link = out['original_link']
            # print("CP4")

            if "https://web.archive.org/web/" in external_link:
                external_link = 'http' + ''.join(external_link.split("http")[-1])

            url = "https://web.archive.org/save/{}".format(external_link)
            out['request_url'] = url

            overwrite = True
            if 'archived_url' in post:
                if not overwrite:
                    if "https://web.archive.org/" in external_link and "are you a robot" not in out['title'].lower():
                        f.write(json.dumps(out))
                        f.write("\n")
                        continue

                print(dir)
                print(f"ATTEMPTING : {url} ({external_link})")
                r = requests.get(url, timeout=1000, allow_redirects=True)

                if r.status_code != 200:
                    print(f"WEB ARCHIVE ERROR: {r.status_code}")
                    f2.write(dir)
                    f2.write("\n")
                    continue

                out['request_response_url'] = r.__dict__['url']
                post['archived_link'] = out['request_response_url']
                post['original_link'] = external_link


            # print("NEWSPAPER")
            n = newspaper(external_link)
            # pprint(n.get_dict)

            out['summary_title'] = n.headline
            out['summary_description'] = n.description
            out['summary_summary'] = n.summary
            out['summary_article'] = n.article
            out['summary_dict'] = n.get_dict

            # print("CPZ")

            f.write(json.dumps(out))
            f.write("\n")

            post['title'] = out['summary_title']
            
            # print("CPY")

            if out['summary_dict']['date_publish']:
                dt =  out['summary_dict']['date_publish'][:10] + "T00:00:00Z"
                post['date'] = dt
            # post['external_link'] = out['request_response_url']

            # print("CPX")

            outline = None
            # tries = 0
            # while tries <= 10:
            #     tries +=1
            #     try:
            #         outline = get_outline2(external_link)
            #         if not outline:
            #             print("OUTLINE SUCCESS!")
            #             break
            #     except:
            #         time.sleep(5 + min(10, 2**tries) + random.random())
            #         pass

            # print(outline)
            if isinstance(outline, str):
                post['article'] = outline
            else:
                post['article'] = max([out['summary_article'], out['summary_summary']], key=len)


            # print("CPA")
            summ = max([out['summary_article'], out['summary_summary']], key=len)
            summ = summ.replace("\n", " ")
            summ_list = summ.split()
            summ_max = 50
            ending = "..." if len(summ_list) >= summ_max else ""
            summ = ' '.join(summ_list[:summ_max]) + ending
            post['summary'] = summ
            # print("CPB")

            fn1 = "../content/media/{}/index.md".format(dir)
            with open(fn1, "w") as f1:
                # print(frontmatter.dumps(post))
                f1.write(frontmatter.dumps(post))

            # print("PRINTING {}".format(fn))

        except Exception as e:
            print("Error in {}: {}".format(dir, str(e)))

        # print(dir)
        # print(out['external_link'])

        # pprint(out)

        # pprint(url)
        # pprint(r.headers)

        # out['request_response'] = r.headers

        # s = summary.Summary(out['external_link'])
        # s.extract()
        # out['summary_title'] = s.title
        # out['summary_description'] = s.description

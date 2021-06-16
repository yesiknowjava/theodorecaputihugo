from newsfetch.news import newspaper
import frontmatter
import os
import requests
from tqdm import tqdm
import json
from pprint import pprint
import random
import datetime

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

with open("missing.txt", "r") as f:
    missing = f.readlines()
    missing = [x.replace("\n", "") for x in missing]

dirs = [x for x in dirs if x not in missing]
random.shuffle(dirs)

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

            post = frontmatter.load(fn)
            out = post.to_dict()

            # out = get_frontmatter(fn)
            out['dir'] = dir

            url = "https://web.archive.org/save/{}".format(out['external_link'])
            out['request_url'] = url
            if "https://web.archive.org/" in out['external_link']:
                f.write(json.dumps(out))
                f.write("\n")
                continue

            print(dir)
            print(f"ATTEMPTING : {url} ({out['external_link']})")
            r = requests.get(url, timeout=100, allow_redirects=True)

            if r.status_code != 200:
                print(f"WEB ARCHIVE ERROR: {r.status_code}")
                f2.write(dir)
                f2.write("\n")
                continue

            out['request_response_url'] = r.__dict__['url']

            # print("NEWSPAPER")
            n = newspaper(out['external_link'])
            # pprint(n.get_dict)

            out['summary_title'] = n.headline
            out['summary_description'] = n.description
            out['summary_summary'] = n.summary
            out['summary_dict'] = n.get_dict

            f.write(json.dumps(out))
            f.write("\n")

            post['title'] = out['summary_title']
            post['summary'] = out['summary_summary'].replace("\n", " ")
            if out['summary_dict']['date_publish']:
                dt =  out['summary_dict']['date_publish'][:10] + "T00:00:00Z"
                post['date'] = dt
            post['external_link'] = out['request_response_url']
            post['original_link'] = out['external_link']
            
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

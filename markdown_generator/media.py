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


with open("media.jsonl", "w") as f:
    for dir in tqdm(dirs):
        try:
            fn = "../content/media/{}/index.md".format(dir)

            post = frontmatter.load(fn)
            out = post.to_dict()

            # out = get_frontmatter(fn)
            out['dir'] = dir

            n = newspaper(out['external_link'])
            out['summary_title'] = n.headline
            out['summary_description'] = n.description
            out['summary_summary'] = n.summary
            out['summary_dict'] = n.get_dict
            
            url = "https://web.archive.org/save/{}".format(out['external_link'])
            print(url)
            r = requests.get(url)
            out['request_url'] = url
            out['request_response_url'] = r.__dict__['url']

            f.write(json.dumps(out))
            f.write("\n")

            post['title'] = out['summary_title']
            post['summary'] = out['summary_summary'].replace("\n", " ")
            dt =  out['summary_dict']['date_publish'][:10] + "T00:00:00Z"
            post['date'] = dt
            post['external_link'] = out['request_response_url']
            post['original_link'] = out['external_link']
            
            fn1 = "../content/media/{}/index.md".format(dir)
            with open(fn1, "w") as f1:
                print(frontmatter.dumps(post))
                f1.write(frontmatter.dumps(post))

            print("PRINTING {}".format(fn))

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

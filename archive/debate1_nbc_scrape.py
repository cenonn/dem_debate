#doesn't work on nbcnews.com :(

import scrape_tools
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
headers = {'user-agent': user_agent}

night1_url = "https://www.nbcnews.com/politics/2020-election/full-transcript-first-democratic-primary-debate-2019-n1022816"
night1_name = "night1.html"

night1_raw = scrape_tools.get_page(night1_url, headers=headers)

night1_html = BeautifulSoup(night1_raw, "html.parser")
#transcript = night1_html.find(id="paragraphs")
transcript = night1_html.find(id="embed-2019-nba-debate-transcript-annotations-wednesday")

#print(night1_html.prettify())
print(transcript)

#for p in night1_html.select('div', {"id": "paragraphs"}):
#    print(p.text)
#    break

#night1_file = open(night1_name, "w")
#night1_file.write(night1_html)
#night1_file.close()


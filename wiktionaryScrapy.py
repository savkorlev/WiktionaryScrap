import scrapy
from scrapy.crawler import CrawlerProcess
import string

inputWord = 'God'

definitions = {}

if inputWord[0] in string.ascii_letters:
    language = 'English'
else:
    language = 'Russian'

class MySpider(scrapy.Spider):
    name = "wiktionarySpider"
    start_urls = [f'https://en.wiktionary.org/wiki/{inputWord}']

    def parse(self, response):

        speechParts = [
            'Article', 'Determiner', 'Numeral', 'Noun', 'Pronoun', 'Verb', 'Adjective', 
            'Adverb', 'Preposition', 'Postposition', 'Circumposition', 'Ambiposition', 
            'Conjunction', 'Interjection', 'Exclamation', 'Particle', 'Clause'
            ]

        for i in range(1, len(response.xpath(f'//h2[span[@id="{language}"]]/following-sibling::*'))):
            
            currentTag = response.xpath(f'//h2[span[@id="{language}"]]/following-sibling::*[{i}]')
            currentTagName = currentTag.get()[currentTag.get().find('<') + 1 : min(currentTag.get().find('>'), currentTag.get().find(' '))]

            if currentTagName == 'h2':
                break

            # elif currentTagName in ['h3', 'h4']:
            elif currentTag.xpath(f'./span[@class="mw-headline"]/text()').get() in speechParts:

                speechPart = currentTag.xpath(f'./span[@class="mw-headline"]/text()').get()
                if speechPart not in definitions:
                    definitions[speechPart] = []

                ols = currentTag.xpath('./following-sibling::ol[1]/li')
                for ol in ols:
                    definitions[speechPart].append(''.join(ol.xpath('.//text()').getall()))

process = CrawlerProcess()
process.crawl(MySpider)
process.start() # the script will block here until the crawling is finished

for speechPart, spPtDefs in definitions.items():
    print(f'\n{speechPart}\n')
    spPtDefs = filter(None, spPtDefs)
    for i, definition in enumerate(spPtDefs):
        if i < 5:  # max 5 definitions per speech part
            print(i + 1)
            print(definition.split('\n')[0])

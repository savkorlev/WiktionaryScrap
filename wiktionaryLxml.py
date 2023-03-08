from lxml import html
import requests
import string

def generateOutput(inputWord: str):

    definitions = {}

    output = inputWord

    speechParts = [
        'Article', 'Determiner', 'Numeral', 'Noun', 'Pronoun', 'Verb', 'Adjective', 
        'Adverb', 'Preposition', 'Postposition', 'Circumposition', 'Ambiposition', 
        'Conjunction', 'Interjection', 'Exclamation', 'Particle', 'Clause'
        ]

    if inputWord[0] in string.ascii_letters:
        language = 'English'
    else:
        language = 'Russian'

    url = requests.get(f'https://en.wiktionary.org/wiki/{inputWord}')
    tree = html.fromstring(url.content)

    for i in range(1, len(tree.xpath(f'//h2[span[@id="{language}"]]/following-sibling::*'))):
        currentTag = tree.xpath(f'//h2[span[@id="{language}"]]/following-sibling::*[{i}]')[0]  # why list
        currentTagName = currentTag.tag

        if currentTagName == 'h2':
            break

        # elif currentTagName in ['h3', 'h4']:
        elif len(currentTag.xpath(f'./span[@class="mw-headline"]')) != 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text in speechParts:

            speechPart = currentTag.xpath(f'./span[@class="mw-headline"]')[0].text
            if speechPart not in definitions:
                definitions[speechPart] = []

            ols = currentTag.xpath('./following-sibling::ol[1]/li')
            for ol in ols:
                definitions[speechPart].append(ol.text_content().split('\n')[0])

    for speechPart, spPtDefs in definitions.items():
        output += f'\n{speechPart}\n'
        # spPtDefs = filter(None, spPtDefs)
        for i, definition in enumerate(spPtDefs):
            if i < 5:  # max 5 definitions per speech part
                output += f'{str(i + 1)}) {definition}\n'

    return output

print(generateOutput('God'))

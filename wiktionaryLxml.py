from lxml import html
import requests
import string


def addPronunciation(tag: str, pronunciations: list, dialects: list):
    tempPronunciations = tag.xpath(f'./following-sibling::ul[1]')[0].text_content().split('\n')
    tempPronunciations = [pronunciation for pronunciation in tempPronunciations if 'IPA(key):' in pronunciation]
    for pronunciation in tempPronunciations:
        dialectStart = pronunciation.find("(") + 1
        dialectEnd = pronunciation.find(")")
        dialect = set(pronunciation[dialectStart:dialectEnd].split(','))

        if 'key' in dialect:
            pronunciations.append(pronunciation[pronunciation.find('IPA(key):') + 10:])

        elif len(dialect.intersection(dialects)) > 0:

            # end of pronunciation
            if pronunciation.rfind('/') > pronunciation.rfind(']'):
                pronunciationStart = pronunciation.find('/')
                pronunciationEnd = pronunciation.rfind('/')
            else:
                pronunciationStart = pronunciation.find('[')
                pronunciationEnd = pronunciation.rfind(']')

            pronunciations.append(pronunciation[dialectStart - 1 : dialectEnd + 1] + ' ' + pronunciation[pronunciationStart : pronunciationEnd + 1])
    
    etymStr = '**Pronunciation**\n\n'
    for pronunciation in pronunciations:
        etymStr += f'{pronunciation}\n\n'

    return etymStr


def addSpeechParts(tag):
    speechPart = tag.xpath(f'./span[@class="mw-headline"]')[0].text
    speechPartStr = f'**{speechPart}**\n\n'

    if tag.xpath('following-sibling::*[1]')[0].tag == 'p':  # class="Latn headword", lang="en"
        underSpeechPart = tag.xpath('following-sibling::*[1]')[0].text_content()
        speechPartStr += f'{underSpeechPart}\n'

    lis = tag.xpath('./following-sibling::ol[1]/li')

    # extract the text from the tag and all its children
    for j, li in enumerate(lis):
        lis[j] = li.text_content().split('\n')[0].strip()

        # usage example if exists
        if len(li.xpath('./dl/dd')) > 0:
            for usageRaw in li.xpath('./dl/dd'):  # alternative: li.xpath('.//div[@class="h-usage-example"]')
                if usageRaw.text_content().split()[0] not in ['Synonym:', 'Synonyms:', 'Antonym:', 'Antonyms:']:
                    usage = usageRaw.text_content()
                    lis[j] += f'\n• *{usage}*'

        elif len(li.xpath('./ol/li/dl/dd')) > 0:
            if li.xpath('./ol/li/dl/dd')[0].text_content().split()[0] not in ['Synonym:', 'Synonyms:', 'Antonym:', 'Antonyms:']:
                usage = li.xpath('./ol/li/dl/dd')[0].text_content()
                lis[j] += f'\n*{usage}*'

    # remove empty entries
    lis = list(filter(None, lis))

    for j, li in enumerate(lis):
        if j < 5:
            speechPartStr += f'{j + 1}) {li}\n\n'

    return speechPartStr


def generateOutput(inputWord: str, speechPart: str):

    output = {}
    speechPart = speechPart.capitalize()
    pronunciations = []
    isPronunBeforeEtym = False
    isPronunFound = False
    isEtymFound = False

    if speechPart == 'All':
        speechParts = [
            'Article', 'Determiner', 'Numeral', 'Noun', 'Pronoun', 'Verb', 'Adjective',
            'Adverb', 'Preposition', 'Postposition', 'Circumposition', 'Ambiposition',
            'Conjunction', 'Interjection', 'Exclamation', 'Particle', 'Clause', 'Proper noun',
            'Participle', 'Phrase'
            ]
    else:
        speechParts = [speechPart]  # break after speechPart is found increases performance

    # IPA(key), (UK), (Received Pronunciation), (Received Pronunciation, General American), (General American), (General American, Canada), (General American, Ireland), (US)
    allDialects = {'UK', 'Received Pronunciation', 'US', 'General American', 'weak vowel merger'}

    if inputWord[0] in string.ascii_letters:
        language = 'English'
    else:
        language = 'Russian'

    url = requests.get(f'https://en.wiktionary.org/wiki/{inputWord}')
    tree = html.fromstring(url.content)

    for i in range(1, len(tree.xpath(f'//h2[span[@id="{language}"]]/following-sibling::*'))):
        currentTag = tree.xpath(f'//h2[span[@id="{language}"]]/following-sibling::*[{i}]')[0]  # why list
        currentTagName = currentTag.tag

        # check what comes first etymology or pronuciation:
        if len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text.split()[0] == 'Etymology':
            isEtymFound = True
            if isPronunFound:
                isPronunBeforeEtym = True
                break
        elif len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text == 'Pronunciation':
            isPronunFound = True
            if isEtymFound:
                break

    for i in range(1, len(tree.xpath(f'//h2[span[@id="{language}"]]/following-sibling::*'))):
        currentTag = tree.xpath(f'//h2[span[@id="{language}"]]/following-sibling::*[{i}]')[0]  # why list
        currentTagName = currentTag.tag

        # terminate if another language has been reached
        if currentTagName == 'h2':
            break
        
        # if etymology comes before pronoun
        if not isPronunBeforeEtym:
            # Etymology
            if len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text.split()[0] == 'Etymology':
                currentEtymology = currentTag.xpath(f'./span[@class="mw-headline"]')[0].text
                output[currentEtymology] = ''

            # Pronunciation
            elif len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text == 'Pronunciation':
                output[currentEtymology] += addPronunciation(currentTag, pronunciations, allDialects)

            # Speech parts
            elif len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text in speechParts:
                output[currentEtymology] += addSpeechParts(currentTag)

        # if pronoun comes before etymology
        else:
            # Pronunciation
            if len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text == 'Pronunciation':
                pronuncations = addPronunciation(currentTag, pronunciations, allDialects)
            
            # Etymology
            elif len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text.split()[0] == 'Etymology':
                currentEtymology = currentTag.xpath(f'./span[@class="mw-headline"]')[0].text
                output[currentEtymology] = pronuncations
            
            # Speech parts
            elif len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text in speechParts:
                output[currentEtymology] += addSpeechParts(currentTag)

    if len(output) == 0:
        if speechPart == 'All':
            output = 'Word or phrase not found'
        else:
            output = 'The word does not fit into the specified part of speech'

    else:
        for key, value in list(output.items()):
            if not value or value[-3] in ['/', ']']:  # TODO: value[-3] is unreliable, better make a list
                del output[key]
        if len(output) == 0:  # TODO: redo this part
            if speechPart == 'All':
                output = 'Word or phrase not found'  # TODO: remove the dynamic typization
            else:
                output = 'The word does not fit into the specified part of speech'

    return output

for key, value in generateOutput('god', 'all').items():
    print(key)
    print(value)

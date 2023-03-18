from lxml import html
import requests
import string

def generateOutput(inputWord: str, speechPart: str):

    output = {}
    speechPart = speechPart.capitalize()

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

        if currentTagName == 'h2':
            break

        # TODO: Pronunciation before etymology aka same pronunciation for all etymologies
        # # Pronunciation
        # elif len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text == 'Pronunciation':
        #     tempPronunciations = currentTag.xpath(f'./following-sibling::ul[1]')[0].text_content().split('\n')
        #     tempPronunciations = [pronunciation for pronunciation in tempPronunciations if 'IPA(key):' in pronunciation]
        #     pronunciations = []
        #     for i, pronunciation in enumerate(tempPronunciations):
        #         dialectStart = pronunciation.find("(") + 1
        #         dialectEnd = pronunciation.find(")")
        #         dialect = set(pronunciation[dialectStart:dialectEnd].split(','))

        #         if 'key' in dialect:
        #             pronunciations.append(pronunciation[pronunciation.find('IPA(key):') + 10:])

        #         elif len(dialect.intersection(allDialects)) > 0:

        #             # end of pronunciation
        #             if pronunciation.rfind('/') > pronunciation.rfind(']'):
        #                 pronunciationStart = pronunciation.find('/')
        #                 pronunciationEnd = pronunciation.rfind('/')
        #             else:
        #                 pronunciationStart = pronunciation.find('[')
        #                 pronunciationEnd = pronunciation.rfind(']')

        #             pronunciations.append(pronunciation[dialectStart - 1 : dialectEnd + 1] + ' ' + pronunciation[pronunciationStart : pronunciationEnd + 1])

            # output = f'{output}**Pronunciation**\n\n'
            # for pronunciation in pronunciations:
            #     output = f'{output}{pronunciation}\n\n'

        # Etymology
        elif len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text.split()[0] == 'Etymology':
            currentEtymology = currentTag.xpath(f'./span[@class="mw-headline"]')[0].text
            output[currentEtymology] = ''

        # Pronunciation
        elif len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text == 'Pronunciation':
            tempPronunciations = currentTag.xpath(f'./following-sibling::ul[1]')[0].text_content().split('\n')
            tempPronunciations = [pronunciation for pronunciation in tempPronunciations if 'IPA(key):' in pronunciation]
            pronunciations = []
            for i, pronunciation in enumerate(tempPronunciations):
                dialectStart = pronunciation.find("(") + 1
                dialectEnd = pronunciation.find(")")
                dialect = set(pronunciation[dialectStart:dialectEnd].split(','))

                if 'key' in dialect:
                    pronunciations.append(pronunciation[pronunciation.find('IPA(key):') + 10:])

                elif len(dialect.intersection(allDialects)) > 0:

                    # end of pronunciation
                    if pronunciation.rfind('/') > pronunciation.rfind(']'):
                        pronunciationStart = pronunciation.find('/')
                        pronunciationEnd = pronunciation.rfind('/')
                    else:
                        pronunciationStart = pronunciation.find('[')
                        pronunciationEnd = pronunciation.rfind(']')

                    pronunciations.append(pronunciation[dialectStart - 1 : dialectEnd + 1] + ' ' + pronunciation[pronunciationStart : pronunciationEnd + 1])
            
            output[currentEtymology] = f'{output[currentEtymology]}**Pronunciation**\n\n'
            for pronunciation in pronunciations:
                output[currentEtymology] = f'{output[currentEtymology]}{pronunciation}\n\n'

        # Speech parts
        elif len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text in speechParts:

            speechPart = currentTag.xpath(f'./span[@class="mw-headline"]')[0].text
            output[currentEtymology] = f'{output[currentEtymology]}**{speechPart}**\n\n'

            if currentTag.xpath('following-sibling::*[1]')[0].tag == 'p':  # class="Latn headword", lang="en"
                underSpeechPart = currentTag.xpath('following-sibling::*[1]')[0].text_content()
                output[currentEtymology] = f'{output[currentEtymology]}{underSpeechPart}\n'

            lis = currentTag.xpath('./following-sibling::ol[1]/li')

            # extract the text from the tag and all its children
            for j, li in enumerate(lis):
                lis[j] = li.text_content().split('\n')[0].strip()

                # usage example if exists
                if len(li.xpath('./dl/dd')) > 0:
                    for usageRaw in li.xpath('./dl/dd'):  # alternative: li.xpath('.//div[@class="h-usage-example"]')
                        if usageRaw.text_content().split()[0] not in ['Synonym:', 'Synonyms:', 'Antonym:', 'Antonyms:']:
                            usage = usageRaw.text_content()
                            lis[j] = lis[j] + '\n' + f'*{usage}*'

                elif len(li.xpath('./ol/li/dl/dd')) > 0:
                    if li.xpath('./ol/li/dl/dd')[0].text_content().split()[0] not in ['Synonym:', 'Synonyms:', 'Antonym:', 'Antonyms:']:
                        usage = li.xpath('./ol/li/dl/dd')[0].text_content()
                        lis[j] = lis[j] + '\n' + f'*{usage}*'

            # remove empty entries
            lis = list(filter(None, lis))

            for j, li in enumerate(lis):
                if j < 5:
                    output[currentEtymology] = f'{output[currentEtymology]}{j + 1}) {li}\n\n'

    if len(output) == 0:
        if speechPart == 'All':
            output = 'Word or phrase not found'
        else:
            output = 'The word does not fit into the specified part of speech'

    return output

qwerty = generateOutput('bow', 'all')
for key, value in qwerty.items():
    print(key)
    print(value)

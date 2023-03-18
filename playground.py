from lxml import html
import requests
import string
import math
import copy

def generateOutput(inputWord: str):

    definitions = {}

    output = inputWord + '\n\n'

    speechParts = [
        'Article', 'Determiner', 'Numeral', 'Noun', 'Pronoun', 'Verb', 'Adjective', 
        'Adverb', 'Preposition', 'Postposition', 'Circumposition', 'Ambiposition', 
        'Conjunction', 'Interjection', 'Exclamation', 'Particle', 'Clause', 'Proper noun',
        'Participle', 'Phrase'
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
        elif len(currentTag.xpath(f'./span[@class="mw-headline"]')) > 0 and currentTag.xpath(f'./span[@class="mw-headline"]')[0].text in speechParts:

            speechPart = currentTag.xpath(f'./span[@class="mw-headline"]')[0].text
            if speechPart not in definitions:
                output += speechPart + '\n'

            if currentTag.xpath('following-sibling::*[1]')[0].tag == 'p':  # class="Latn headword", lang="en"
                underSpeechPart = currentTag.xpath('following-sibling::*[1]')[0].text_content()
                output += underSpeechPart

            lis = currentTag.xpath('./following-sibling::ol[1]/li')

            # extract the text from the tag and all its children
            for j, li in enumerate(lis):
                lis[j] = li.text_content().split('\n')[0].strip()
                # usage example if exists
                if len(li.xpath('.//*[@class = "h-usage-example"]')) > 0:
                    for usageI in range(len(li.xpath('.//*[@class = "h-usage-example"]'))):

                        usageExample = li.xpath('.//*[@class = "h-usage-example"]')[usageI].text_content()
                        tempSUE = usageExample.split()
                        separatedUsageExample = copy.deepcopy(tempSUE)

                        maxLength = 70
                        splitNrs = math.floor(len(usageExample) / maxLength)
                        currentLength = len(tempSUE) - 2

                        if splitNrs > 0:
                            currentSplit = 1
                            for k, element in enumerate(tempSUE):
                                currentLength += len(element)
                                if currentLength > currentSplit * maxLength:
                                    currentSplit += 1
                                    separatedUsageExample[k-1] = separatedUsageExample[k-1] + '\n\t'
                            lis[j] = lis[j] + '\n\t' + ' '.join(separatedUsageExample)

                        else:
                            lis[j] = lis[j] + '\n\t' + usageExample

                            # for splitNr in range(splitNrs + 1):
                            #     separatedUsageExample = separatedUsageExample + usageExample[(splitNr)*maxLength:(splitNr+1)*maxLength].strip()
                            #     if splitNr < splitNrs:
                            #         separatedUsageExample = separatedUsageExample + '\n\t'
                        # if len(separatedUsageExample) > 0:
                        #     lis[j] = lis[j] + '\n\t' + separatedUsageExample
                        # else:
                        #     lis[j] = lis[j] + '\n\t' + usageExample

            # remove empty entries
            lis = list(filter(None, lis))

            for j, li in enumerate(lis):
                if j < 5:
                    output = f'{output}{j + 1}) {li}\n'
            output += '\n'

    if output.replace('\n', '') == inputWord:
        output = 'Word or phrase not found'

    return output

print(generateOutput('God'))

test = {'Etymology1': ''}
print(test['Etymology1'][-1])

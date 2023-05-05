import requests
import feedparser
import hashlib
from bs4 import BeautifulSoup

urls = []

savedImages = []
savedImageFile = 'SavedImageHashes.txt'
baseFilePath = './Images/'

illegalFilepathCharacters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

urls.append('https://www.reddit.com/r/memes/.rss?limit=100')

def GetPreviousHashes():
    global savedImages, savedImageFile

    print('Getting previous image hashes')

    f = open(savedImageFile)
    savedImages = f.read().splitlines()
    f.close()

    print('Found {} previously saved image hashes'.format(len(savedImages)))
    print('\n')

def UpdateHashes():
    global savedImages, savedImageFile

    print('Updating saved file')
    f = open(savedImageFile, 'w')

    for hash in savedImages:
        f.writelines(hash + '\n')
    f.close()

    print('Updated saved file')

def Main(urls):
    global savedImages

    GetPreviousHashes()

    for url in urls:
        print("Beginning download for: {}".format(url))
        print('\n')

        feed = feedparser.parse(url)

        for post in feed.entries:
            
            soup = BeautifulSoup(post.content[0].value, 'html.parser')
            fileName = RemoveIllegalFilepathCharacters(post.title)
            fileUrl = soup.find('span').find('a').get('href')

            print('Saving:')
            print('Name: ' + fileName)
            print('Url: ' + fileUrl)

            SaveFile(fileName, fileUrl)

    UpdateHashes()

def SaveFile(fileName, fileUrl):
    global savedImages, baseFilePath

    try:
        response = requests.get(fileUrl)
        extension = response.headers['content-type'].split('/')[1]

    except:
        print('Url was invalid and could not be requested {}'.format(fileUrl))
        return

    if(not IsImage(extension)):
        print('{fileName} was not a image it was {extension} and has not been saved'.format(fileName = fileName, extension = extension))
        print('\n')
        return

    fileHash = hashlib.md5(response.content).hexdigest()

    if(fileHash not in savedImages):
        try:
            f = open('{baseFilePath}{name}_{hash}.{extension}'.format(baseFilePath = baseFilePath, name = fileName, hash = fileHash, extension = extension), 'wb')
            f.write(response.content)
            f.close()
        except:
            print('The file could not be saved! {}'.format(fileName))
            return

        savedImages.append(fileHash)
    else:
        print('{fileName} is a duplicate! and will not be saved again'.format(fileName = fileName))
        print('\n')
    print('\n')
    
def IsImage(extension):
    if('html' in extension or 'charset' in extension):
        return False
    return True


def RemoveIllegalFilepathCharacters(fileName):
    global illegalFilepathCharacters

    sanitizedFilename = fileName

    for character in illegalFilepathCharacters:
        sanitizedFilename = sanitizedFilename.replace(character, '')
    
    return sanitizedFilename

Main(urls)
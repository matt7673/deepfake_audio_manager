import PySimpleGUI as sg
import guiFunctions
from elevenlabslib.helpers import *
from elevenlabslib import *
import os

sg.theme('DarkBlue14') 

# make sure user has an API key
def loginUser():
    # login user
    tempPath = os.path.dirname(os.path.realpath(__file__))
    basePath = os.path.dirname(os.path.realpath(tempPath))
    keyPath = basePath + '/apiKey.txt'
    while True:
        # user has environmental key value
        if "apiKey" in os.environ:
            apiKey = os.environ.get('apiKey')
        else:
            # first time, creating key
            if not os.path.exists(keyPath):
                apiKey = guiFunctions.keyPrompt()

            # user is using key file 
            else:
                with open(keyPath, 'r') as file:
                    apiKey = file.read().replace('\n', ' ')


        user = ElevenLabsUser(apiKey)
        print(user)
        # verify user
        try:
            user.get_current_character_count()
            with open(keyPath, 'w') as file:
                file.write(apiKey)
        except requests.exceptions.HTTPError:
            guiFunctions.messageBox("Key is invalid.")
            continue
        
        return user

def getUser():
    if getUser.user == None:
        getUser.user = loginUser()
        
    return getUser.user

getUser.user = None

if __name__ == '__main__':
    guiFunctions.mainPage()
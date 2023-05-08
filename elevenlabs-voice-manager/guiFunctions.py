import PySimpleGUI as sg
import profileFunctions
import os
from elevenlabslib.helpers import *
from elevenlabslib import *
from sys import platform

from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio

sg.theme('DarkGrey2') 
font = ("Arial", 16)

def messageBox(message):
    ''' displays a message box informing user on result of action
    message: string, message to be displayed'''

    layout = [[sg.Text(f"{message}", font=font)], [sg.Button("Ok", size=(10,0), font=font)]]

    #Building Window
    window = sg.Window('', layout, auto_size_text=True, resizable=True)
        
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Ok":
            break
        window.bring_to_front()

    window.close()

def keyPrompt():
    ''' display box for user to enter their elevenlabs api key
    returns: string, elevenlabs api key'''

    layout = [[sg.Text(f"Please enter your ElevenLabs API key", font=font)], 
              [sg.Input(size=(None, 10), expand_x=True, enable_events=True, key='send', font=font)],
              [sg.Button("Submit", size=(10,0), font=font)]]

    #Building Window
    window = sg.Window('', layout, auto_size_text=True, resizable=True)
        
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            window.close()
            exit()

        elif event == "Submit":
            apiKey = values['send']
            break

        window.bring_to_front()

    window.close()
    return apiKey

def questionBox(message):
    ''' displays a message box asking if user wishes to proceed
    message: string, message to be displayed
    returns True if user accepts, false if not'''

    layout = [[sg.Text(f"{message}", font=font)], [sg.Button("Ok", size=(10,0), font=font)], [sg.Button("Cancel", size=(10,0), font=font)]]

    #Building Window
    window = sg.Window('', layout, auto_size_text=True, resizable=True)
    
    accept = False
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Cancel":
            break
        elif event == "Ok":
            accept = True
            break
        window.bring_to_front()

    window.close()
    return accept

def playAudioButton(event, window, fileNames, filePaths, playback):
    button = window[event]

    def updateButtons():
        # update all buttons except current
        for fileName in fileNames:
            if fileName != event:
                tempButton = window[fileName]
                if tempButton.ButtonText == 'Stop':
                    tempButton.update(text='Play')

    # make sure audio is not already playing
    if button.ButtonText == 'Play':
        updateButtons()

        if playback != None and playback.is_playing():
            playback.stop()

        index = fileNames.index(event)
        audioFile = filePaths[index]
        # play_audio_bytes(open(scriptAudio,"rb").read(),False
        button.update(text='Stop')

        try:
            # Start playing the audio in the background
            audio = AudioSegment.from_file(audioFile)
            playback = _play_with_simpleaudio(audio)
        except Exception as e:
            sg.popup_error(f"Unable to play audio file: {audioFile}")
            button.update(text='Play')
    
    else:
        button.update(text='Play')
        playback.stop()

    return playback

def selectScriptsForDownload(scriptNames):
    ''' Gives users a window with two listboxes to select which text files will be given for upload. Text files can be edited and added here too.
    scriptNames: list, all script names currently in scripts directory
    returns list of script names user chose or None if they canceled the operation
    '''

    uploadScriptNames = []
    col1 = [[sg.Text(f"Scripts to use for generation", font=font)],
            [sg.Listbox(uploadScriptNames, expand_x=True, expand_y=True, select_mode = sg.LISTBOX_SELECT_MODE_SINGLE, key='uploadScriptNames', enable_events=True, font=font)]]
    col2 = [[sg.Text(f"Available scripts", font=font)],
            [sg.Listbox(scriptNames, expand_x=True, expand_y=True, select_mode = sg.LISTBOX_SELECT_MODE_SINGLE, key='scriptNames', enable_events=True, font=font)]]
    bottomRow = [sg.Button("Generate", size=(40,0), font=font), sg.Button("Cancel", size=(40,0), font=font)]



    layout = [[sg.Text("Selection:", font=font), sg.Input(size=(None, 10), readonly=True, expand_x=True, enable_events=True, key='search', disabled_readonly_background_color=sg.theme_input_background_color(),font=font), 
               sg.Button('Add to upload', auto_size_button=True, font=font, key='edit'), sg.Button('View', auto_size_button=True, font=font)],
            [sg.Column(col1, element_justification="c", expand_y=True, expand_x=True, key='uploadScriptNames'), sg.Column(col2, element_justification="c", expand_y=True, expand_x=True, key='scriptNames',)],
            bottomRow]

    # create window
    window = sg.Window('Select scripts for generation', layout, element_justification='c', size=(1200, 700), resizable=True)

    button = window['edit']
    while True:
        event, values = window.read()
        scriptName = values['search']
        

        if event in (sg.WIN_CLOSED, 'Cancel'):   # always check for closed window
            uploadScriptNames = None
            break

        if event == 'Generate':
            break

        if (event == 'scriptNames' and values['scriptNames']) or (event == 'uploadScriptNames' and values['uploadScriptNames']):
            scriptName = values['scriptNames'][0] if (event == 'scriptNames') else values['uploadScriptNames'][0]
           
            window['search'].update(scriptName)
            if scriptName not in uploadScriptNames:
                button.update(text='Add to upload')
            else:
                button.update(text='Remove from upload')
        
        if scriptName: #and (values['uploadScriptNames'] or values['scriptNames']):
            if event == 'View':
                scriptsPath = profileFunctions.scriptsPath
                scriptPath = scriptsPath + f'/{scriptName}'
                editScript(scriptPath, scriptsPath)
                scriptNames = profileFunctions.listdir_nohidden(scriptsPath)
                window['scriptNames'].update(scriptNames)
        
            if event == 'edit':
                if scriptName in uploadScriptNames:
                    uploadScriptNames.remove(scriptName)
                    button.update(text='Remove from upload')
                else:
                    uploadScriptNames.append(scriptName)
                    button.update(text='Add to upload')

                window['uploadScriptNames'].update(uploadScriptNames)
                if scriptName not in uploadScriptNames:
                    button.update(text='Add to upload')
                else:
                    button.update(text='Remove from upload')
                
        window.bring_to_front()

    window.close()
    return uploadScriptNames

def reuploadElevenLabsProfile(voiceObj, voiceName):
    profileFunctions.removeFromEL(voiceObj)
    voiceObj = None
    # check if new profile can be made
    if not profileFunctions.canCloneVoice():
        messageBox('No space left on ElevenLabs account. Please remove a voice by selecting one currently uploaded to ElevenLabs then selecting "Remove from ElevenLabs".')
    else:
        voiceObj = uploadProfile(voiceName)
    return voiceObj


def viewAudioFiles(src, voiceName, voiceObj, canRegen):
    """ creates a window displaying audio files for user to select and listen to
    scriptNames: list, name of audio files"""
    

    while True:
        # create list of script audio files
        scriptNames = profileFunctions.listdir_nohidden(src)
        # create lists for storing script audio file paths
        scriptPaths = []
        # fill list of script audio file paths
        for scriptName in scriptNames:
            scriptPath = src + scriptName
            scriptPaths.append(scriptPath)

        col = []  
        # add script names to column
        bottomRow = [sg.Button("Return", size=(40,0), font=font), sg.Button("Add samples", size=(40,0), font=font)]
        if canRegen:
            bottomRow.pop(1)

        for scriptName in scriptNames: 
            row = [sg.Button(scriptName, expand_x=True,font=font, disabled=True, key='label'), sg.Button('Play', auto_size_button=True, font=font, key=scriptName)]
            if canRegen:
                row += [sg.Button('Regenerate', auto_size_button=True, font=font, key=f'regen{scriptName}'), sg.Button('Edit script', auto_size_button=True, font=font, key=f'edit{scriptName}')]

            col.append(row)


        layout = [[sg.Text(f'Select file for playback', font=font)], 
                [sg.Text(f"Characters remaining: {profileFunctions.getCharactersLeft()}", key="chars", font=font)],
                [sg.Column(col, scrollable=True, vertical_scroll_only=True, element_justification="c", expand_y=True, expand_x=True)],
                bottomRow]

        # create window
        window = sg.Window('Playback selection', layout, element_justification='c', size=(1200, 700), resizable=True)

        playback = None
        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, 'Return'):   # always check for closed window
                window.close()
                if playback != None and playback.is_playing():
                    playback.stop()
                return

            elif 'regen' in event:
                scriptName = event[5:len(event)-4] # remove unneeded bits
                # get string for audio file user is on
                scriptStringList = profileFunctions.getScriptListFromAudioFile(scriptName)
                # send the script to be processed by elevenlabs
                profileFunctions.downloadScripts(scriptStringList, [scriptName], voiceName, voiceObj)
                # update characters
                window["chars"].update(f"Characters remaining: {profileFunctions.getCharactersLeft()}")

            elif 'edit' in event:
                scriptName = event[4:len(event)-4] # remove unneeded bits
                scriptName += '.txt'
                scriptsPath = profileFunctions.scriptsPath
                scriptPath = scriptsPath + f'/{scriptName}'
                editScript(scriptPath, scriptsPath)
            
            elif event in scriptNames: # get index from event choice and play audio
                playback = playAudioButton(event, window, scriptNames, scriptPaths, playback)
            
            elif event == 'Add samples':
                dest = profileFunctions.voiceProfilePath + f'/{voiceName}/samples'
                profileFunctions.addToDirectory(dest)
                break
            window.bring_to_front()
        
    

def uploadProfile(voiceName):

    chosenSamples = []
    # path for storing samples
    samplePath = profileFunctions.voiceProfilePath + f'/{voiceName}/samples/'

    while True:
        # get list of sample file names
        sampleNames = profileFunctions.listdir_nohidden(samplePath)
        col = []  
        # create list of sample file paths 
        samplePaths = []
        for sampleName in sampleNames:
            tempSamplePath = samplePath + sampleName
            samplePaths.append(tempSamplePath)
            if tempSamplePath in chosenSamples:
                buttonText = 'Remove'
            else:
                buttonText = 'Add'

            row = [sg.Button(sampleName, expand_x=True,font=font, disabled=True, key='label'), sg.Button('Play', auto_size_button=True, font=font, key=sampleName), 
                    sg.Button(buttonText, auto_size_button=True, font=font, key=f'edit{sampleName}')]
            bottomRow = [sg.Button("Submit", size=(40,0), font=font), sg.Button("Cancel", size=(40,0), font=font), sg.Button("Add samples", size=(40,0), font=font)]

            # add script names to column
            col.append(row)


        layout = [[sg.Text(f'Select file for playback', font=font)], 
                [sg.Column(col, scrollable=True, vertical_scroll_only=True, element_justification="c", expand_y=True, expand_x=True)],
                bottomRow]

        # create window
        window = sg.Window('Playback selection', layout, element_justification='c', size=(1200, 700), resizable=True)

        playback = None
        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, 'Cancel'):   # always check for closed window
                if playback != None and playback.is_playing():
                    playback.stop()
                window.close()
                return None

            elif 'edit' in event:
                button = window[event]

                scriptName = event[4:] # remove unneeded bits
                index = sampleNames.index(scriptName)
                samplePath = samplePaths[index]
                
                if button.ButtonText == 'Add':
                    chosenSamples.append(samplePath)
                    button.update(text='Remove')
                elif button.ButtonText == 'Remove':
                    chosenSamples.remove(samplePath)
                    button.update(text='Add') 
            
            elif event == 'Submit':
                if playback != None and playback.is_playing():
                    playback.stop()
                window.close()
                voiceObj = profileFunctions.uploadToEL(chosenSamples, voiceName)  
                return voiceObj
                        
            elif event in sampleNames: # get index from event choice and play audio
                playback = playAudioButton(event, window, sampleNames, samplePaths, playback)
            
            elif event == 'Add samples':
                dest = profileFunctions.voiceProfilePath + f'/{voiceName}/samples'
                profileFunctions.addToDirectory(dest)
                break
            window.bring_to_front()

def getProfileName():
    ''' display box for user to enter the profile name when creating a new profile
    returns: string, profile name'''

    layout = [[sg.Text(f"Please enter the name of the profile.", font=font)], 
              [sg.Input(size=(None, 10), expand_x=True, enable_events=True, key='send', font=font)],
              [sg.Button("Submit", size=(10,0), font=font),sg.Button("Cancel", size=(10,0), font=font)]]

    #Building Window
    window = sg.Window('', layout, auto_size_text=True, resizable=True)
        
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            name = None
            break

        elif event == "Submit":
            name = values['send']
            name = profileFunctions.cleanUpString(name)
            if name not in profileFunctions.listdir_nohidden(profileFunctions.voiceProfilePath):
                break
            messageBox('Name already exists.')

        window.bring_to_front()

    window.close()
    return name

def getPathToSrc():
    '''Creates a window for user to select folder to draw files from
    returns src path'''

    layout = [[sg.Text("Directory path: ", font=font), sg.Input(key="display" ,change_submits=True, font=font), sg.FolderBrowse(key="selection", font=font)],
               [sg.Button("Submit", size=(10,0), font=font)], [sg.Button("Cancel", size=(10,0), font=font)]]

    ###Building Window
    window = sg.Window('Copy Samples', layout, size=(1100,500), resizable=True)
        
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Cancel":
            src = None
            break

        elif event == "Submit":
            src = values["selection"]
            break
        window.bring_to_front()
        
    window.close()
    return src

def viewAndEditScripts(scriptsPath):
    """ creates a window displaying script text files for selection
    scriptNames: list of text file names
    returns name of text file or None if canceled""" 
    
    while True:
        scriptNames = profileFunctions.listdir_nohidden(scriptsPath)
        # build layout
        col = []  
        # add script names to column
        for scriptName in scriptNames: 
            col.append([sg.Button(scriptName, size=(60,0), font=font)])
        
        layout = [[sg.Text(f'Select file for editing', font=font)], 
                [sg.Column(col, scrollable=True, vertical_scroll_only=True, element_justification="r", size=(600,600))],
                [sg.Button("Create new script", size=(40,0), font=font), sg.Button("Copy from directory", size=(40,0), font=font), sg.Button("Return", size=(40,0), font=font)]]

        # create window
        window = sg.Window('Local scripts', layout, element_justification='c', size=(1200, 700), resizable=True)

        scriptName = None
        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, 'Return'):   # always check for closed window
                window.close()
                return
            
            elif event == 'Create new script':
                editScript(None, scriptsPath)
                break

            elif event == 'Copy from directory':
                profileFunctions.addToDirectory(profileFunctions.scriptsPath)
                break

            elif event in scriptNames: # get name of text file
                scriptPath = scriptsPath + f'/{event}'
                editScript(scriptPath, scriptsPath)
                break
            window.bring_to_front()

        window.close()

def editScript(scriptPath, scriptsPath):
    """ creates window for editing script file"""

    # open file and get string if file exists
    if scriptPath != None:
        with open(scriptPath, 'r') as file:
            script = file.read().replace('\n', ' ')
        finalRow= [sg.Text("File name: ", font=font), sg.Input(expand_x=True, enable_events=True, key='saveName', font=font), sg.Button("Save as new file", font=font, key='saveNew'), sg.Button('Save', font=font), sg.Button('Cancel', font=font)]
        
    else:
        script = ''
        finalRow = [sg.Text("File name: ", font=font), sg.Input(expand_x=True, enable_events=True, key='saveName', font=font), sg.Button("Save as new file", font=font, key='saveNew'), sg.Button('Cancel', font=font)]

    # build layout
    # profile selection layout
    layout = [[sg.Text("Script editor", key="header", font=font)],
            [sg.Multiline(expand_x=True, expand_y=True, enable_events=True, key='edit', font=font, default_text=script, no_scrollbar=True)],
            finalRow]
    
    
    
    window = sg.Window('Editing file', layout, element_justification="c", size=(1100, 500), resizable=True)
    
    # Event Loop
    while True:
        event, values = window.read()
   
        if event in (sg.WIN_CLOSED, 'Cancel'):                # always check for closed window
            break

        elif event == 'saveNew':
            fileName = values['saveName']
            if fileName != '':   
                fileName = profileFunctions.cleanUpString(fileName)
                if '.txt' not in fileName:
                    fileName += '.txt'

                newScriptPath = scriptsPath + f'/{fileName}'
                
                with open(newScriptPath, 'w') as f:
                    f.write(values['edit'])
                break
            else:
                messageBox('Text field for file name is empty')

        elif event == 'Save':
            with open(scriptPath, 'w') as f:
                f.write(values['edit'])
            break
        
        window.bring_to_front()
    window.close()

# function for displaying of profile window
def profileWindow(voiceName, voiceObj):

    finished = False
    while not finished:
        if voiceObj: # options for when voice is on elevenlabs
            options = ["Manage local samples", "Manage generated audio", "Generate and download audio",  "Reupload profile", "Remove profile from ElevenLabs", "Return"]
            status = "uploaded"
        else: # options for when voice is not on elevenlabs
            options = ["Manage local samples", "Manage generated audio", "Upload profile to ElevenLabs", "Return"]
            status = "not uploaded"

        layout = [[sg.Text(f'Profile for {voiceName}', font=font)], [sg.Text(f'Currently {status} to ElevenLabs', font=font)]]
        
        # add options to layout
        for option in options: 
            layout.append([sg.Button(option, size=(40,0), font=font)])

        # create window
        window = sg.Window('Voice profile', layout, element_justification='c', size=(700, 500), resizable=True)

        # event loop
        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, 'Return'):   # always check for closed window
                finished = True
                break
            
            # on elevenlabs
            elif event == "Generate and download audio":
                profileFunctions.downloadAllScripts(voiceName, voiceObj)

            elif event == 'Remove profile from ElevenLabs':
                profileFunctions.removeFromEL(voiceObj)
                voiceObj = None
                break
            
            elif event == 'Reupload profile':
                if questionBox('Profile will be removed when starting this operation. Continue?'):
                    voiceObj = reuploadElevenLabsProfile(voiceObj, voiceName)
                break

            # not on eleven labs
            elif event == "Upload profile to ElevenLabs":
                # check if new profile can be made
                if not profileFunctions.canCloneVoice():
                    messageBox('No space left on ElevenLabs account. Please remove a voice by selecting one currently uploaded to ElevenLabs then selecting "Remove from ElevenLabs".')
                else:
                    voiceObj = uploadProfile(voiceName)
                    break

            #shared
            elif event == "Manage local samples":
                profileFunctions.viewAndPlayAudio(voiceName, voiceObj, "samples")

            elif event == "Manage generated audio":
                profileFunctions.viewAndPlayAudio(voiceName, voiceObj, "generatedAudio")

            window.bring_to_front()
        
        window.close()

def mainPage():
    toggle = True
    names = profileFunctions.getProfileNames(toggle)

    # profile selection layout
    layout = [[sg.Text("All profiles", key="header", font=font)],
            [sg.Text(f"Characters remaining: {profileFunctions.getCharactersLeft()}", key="chars", font=font)],
            [sg.Text("Search:", font=font), sg.Input(size=(None, 10), expand_x=True, enable_events=True, key='search', font=font)],
            [sg.Listbox(names, expand_x=True, expand_y=True, select_mode = sg.LISTBOX_SELECT_MODE_SINGLE, key='names', font=font)],
            [sg.Button("Select profile", font=font), sg.Button('Create new profile', font=font), sg.Button('Manage scripts', font=font),
             sg.Button('List profiles on ElevenLabs', font=font, key='mode'), sg.Button('Exit', font=font)]]
    
    window = sg.Window('Profile selection', layout, element_justification="c", size=(1100, 500), resizable=True)

    # Event Loop
    while True:
        event, values = window.read()
   
        if event in (sg.WIN_CLOSED, 'Exit'):                # always check for closed window
            break
        elif event == 'Create new profile':
            info = profileFunctions.createVoiceProfile()
            if info is not None:
                voiceName = info[0]
                voiceObj = info[1]
                profileWindow(voiceName, voiceObj)

        elif event == 'mode': # changes window title and button to reflect mode
            header =  "Profiles uploaded to ElevenLabs" if toggle else "All profiles"
            switch = "List all profiles" if toggle else "List profiles on ElevenLabs"

            window.Element('header').Update(header)
            toggle = not toggle
            # get new list of profiles
            window['mode'].update(switch)
            
        elif event == 'Manage scripts':
            profileFunctions.manageScripts()

        # if a list item is chosen
        elif event == 'Select profile': 
            try:
                voiceName = values['names'][0]
                voiceObj = profileFunctions.getVoiceObject(voiceName)
                profileWindow(voiceName, voiceObj)

            except IndexError:
                pass

        if values['search'] != '':                         # if a keystroke entered in search field
            search = values['search']
            new_values = [x for x in names if search.lower() in x.lower()]  # do the filtering
            window['names'].update(new_values)     # display in the listbox
        else:
            # display original unfiltered list
            names = profileFunctions.getProfileNames(toggle)
            window['names'].update(names)
        window["chars"].update(f"Characters remaining: {profileFunctions.getCharactersLeft()}")
        window.bring_to_front()

    window.close()
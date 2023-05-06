from elevenlabslib.helpers import *
from elevenlabslib import *
import os
import shutil
import guiFunctions
import main
from pydub import AudioSegment

# get path to where directory lives and enter voiceProfiles directory
tempPath = os.path.dirname(os.path.realpath(__file__))
basePath = os.path.dirname(os.path.realpath(tempPath))
voiceProfilePath = basePath + '/voiceProfiles'
scriptsPath = basePath + '/scripts'
print(scriptsPath)

# always test to see if required directories are present
if not os.path.exists(voiceProfilePath):
    os.makedirs(voiceProfilePath)
if not os.path.exists(scriptsPath):
    os.makedirs(scriptsPath)

maxVoices = 10

def getCharactersLeft():
    if getCharactersLeft.char == None:
        updateCharactersLeft()
    return getCharactersLeft.char   

def updateCharactersLeft():
    ''' Calculates and returns the total amount of characters left the user has.'''
    usedChars = main.getUser().get_current_character_count()
    totalChars = main.getUser().get_character_limit()
    getCharactersLeft.char = totalChars - usedChars

getCharactersLeft.char = None

def enoughCharsForOperation(script):
    ''' Checks if there are enough characters left to successfully complete the operation.'''
    return getCharactersLeft() > len(script)


def listdir_nohidden(path):
    """used for getting list of files without any unwanted additions
    files: list, list of files to return"""
    files = []
    for file in os.listdir(path):
        if not file.startswith('.'):
            files.append(file)

    return files

def cleanUpString(string):
    return string.replace(" ", "")

def canCloneVoice():
    '''Checks if the max number of voices has been reached'''

    voiceObjs = main.getUser().get_available_voices()
    voiceNames = []

    # fill list of voice names and voice profiles with only cloned voices
    for voiceObj in voiceObjs:
        if isinstance(voiceObj, ElevenLabsClonedVoice):
            voiceNames.append(voiceObj.get_name())

    return len(voiceNames) != maxVoices

# finds a voice object matching the voiceName, if one exists, on elevenlabs
# returns elevenlabsVoiceObject or None if no matching object was voice
def getVoiceObject(voiceName):
    voiceObjs = main.getUser().get_available_voices()

    # search voices on elevenlabs and return match, only considers cloned voices
    for voiceObj in voiceObjs:
        if isinstance(voiceObj, ElevenLabsClonedVoice) and voiceObj.get_name() == voiceName:
            return voiceObj

    return None

def getScriptListFromAudioFile(audioFileName):
    scriptStringList = []
    for script in os.listdir(scriptsPath):
        scriptName = script[:len(script)-4] # remove .txt
        
        if scriptName == audioFileName:
            print(f'matching script {scriptName}')
            scriptPath = scriptsPath + f'/{script}'
            with open(scriptPath, 'r') as file:
                script = file.read().replace('\n', ' ')
                scriptStringList.append(script)
            print(scriptStringList)
            return scriptStringList
    
    

def downloadAllScripts(voiceName, voiceObj):
    """function for generating and downloading audio using provided scripts
    voiceName: string, name of voice
    voiceObj: ElevenLabsVoiceObject"""

    overwrite = True # WIP
    
    # get all text files in script directory and create a list of strings
    scriptStringList = []
    scriptNames = listdir_nohidden(scriptsPath)
    for scriptName in scriptNames:
        # read script file 
        scriptPath = scriptsPath + f'/{scriptName}'
        with open(scriptPath, 'r') as file:
            script = file.read().replace('\n', ' ')
            scriptStringList.append(script)

    downloadScripts(scriptStringList, scriptNames, voiceName, voiceObj, overwrite)

def downloadScripts(scriptStringList, scriptNames, voiceName, voiceObj, overwrite):
    ''' download 
    scriptStringList: list of strings, list of scripts
    scriptNames: list of strings, names of scripts
    voiceName: string, name of the voice to use
    voiceObj: elevenlabs voice object
    overwrite: bool, wether or not to overwrite current file
    '''

    downloadsPath = voiceProfilePath + f"/{voiceName}/generatedAudio"

    # create directory for saving sound files if one doesnt exist
    if not os.path.exists(downloadsPath):
        os.makedirs(downloadsPath)


    # upload each string to elevenlabs to generate audio, then save as wav file
    while True:
        for i, script in enumerate(scriptStringList):
            if not enoughCharsForOperation(script):
                guiFunctions.messageBox("""You do not have enough characers to continue this operation. Either upgrade your account or wait until you have access to more.""")
                return
            
            audioData = voiceObj.generate_audio_bytes(script.strip()) # elevenlabs upload
            name = scriptNames[i]
            if '.txt' in name:
                name = name[:len(name)-4] # remove .txt
            # scriptPath = downloadsPath + f"/{name}.wav"

            # # save audio to wav file
            # if overwrite or (not os.path.exists(scriptPath)):
            #     with open(scriptPath, mode='bw') as file:
            #         file.write(audioData)

            scriptPath = downloadsPath + f"/{name}.wav"

            # save audio to wav file
            if overwrite or (not os.path.exists(scriptPath)):
                # Load the audio data
                audio = AudioSegment.from_file(io.BytesIO(audioData), format="mp3")
                
                # Set the audio parameters
                audio = audio.set_frame_rate(44100).set_channels(1).set_sample_width(2)

                # Export to WAV format
                audio.export(scriptPath, format="wav")
        
        break
    updateCharactersLeft()
    guiFunctions.messageBox("Download finished")

def viewAndPlayAudio(voiceName, voiceObj, location):
    """function for giving user ability to view and play script audio that has been downloaded
    voiceName: string, name of voice
    location: string, directory to search, will either be generatedAudio or samples"""

    # adds button for regenerating a specific audio sample
    canRegen = (location == "generatedAudio") and (voiceObj != None)

    # create path to directory containing downloaded script files
    downloadsPath = voiceProfilePath + f"/{voiceName}/{location}/"

    # make filepath and create directory for storing downloads if it does not exist
    if not os.path.exists(downloadsPath):
        os.makedirs(downloadsPath)

    # create list of script audio files
    scriptNames = listdir_nohidden(downloadsPath)

    # create lists for storing script audio file paths
    scriptPaths = []

    # fill list of script audio file paths
    for scriptName in scriptNames:
        scriptPath = downloadsPath + scriptName
        scriptPaths.append(scriptPath)

    # pass info to GUI function to create window
    guiFunctions.viewAudioFiles(scriptNames,scriptPaths, voiceName, voiceObj, canRegen)

def removeFromEL(voiceObj):
    '''Removes voice from ElevenLabs'''
    main.getUser().get_voices_by_name(voiceObj.get_name())[0].delete_voice()


def uploadToEL(samplePaths, voiceName):
    '''upload voice to eleven labs
    voiceName: string, name of voice
    returns ElevenLabsVoice object or None if one wasn't able to be created'''
    
    voiceObj = None
    # upload sample to eleven labs
    if len(samplePaths) > 0:
        # uploading new voice profile
        for i in range(10):
            try:
                # create voice clone
                voiceObj = main.getUser().clone_voice_by_path(voiceName, samplePaths)
                guiFunctions.messageBox('Voice profile successfully uploaded to ElevenLabs.')
                break

            except requests.exceptions.RequestException:
                pass

    # if voice object has no value alert user 
    if not voiceObj:
        guiFunctions.messageBox('Profile was unable to be uploaded to eleven labs. Please try again later.')
    
    return voiceObj             

def createVoiceProfile():
    '''Creates new directory for voice in voiceProfiles and clones voice on ElevenLabs
    returns list, [voiceName, voiceObj]'''

    # check if new profile can be made
    if not canCloneVoice():
        guiFunctions.messageBox('No space left on ElevenLabs account. Please remove a voice by selecting one currently uploaded to ElevenLabs then selecting "Remove from ElevenLabs".')
        return
    info = guiFunctions.getSamples(True)
    if info is None:
        return
    
    voiceName = cleanUpString(info[0])
    orgSamplePath = info[1]

    if orgSamplePath not in (None, ''):
        copyToSamplesDirectory(voiceName, orgSamplePath, True)
        voiceObj = uploadToEL(voiceName)

    else:
         # path for storing samples
        samplePath = voiceProfilePath + f'/{voiceName}/samples'

        # make filepath and create directory for storing samples since it does not exist
        if not os.path.exists(samplePath):
            os.makedirs(samplePath)

        guiFunctions.messageBox("""A profile was created, however a directory containing samples must be selected to upload to ElevenLabs. Once you have a directory of samples
                               add them to the profile with "Add samples to profile directory" and then try uploading again.""")
        voiceObj = None
    
    return [voiceName, voiceObj]

def addToSamplesDirectory(voiceName):
    # get sample path from user
    orgSamplePath = guiFunctions.getSamples(False)

    if orgSamplePath == None:
        return 

    orgSamplePath = orgSamplePath[1]

    if orgSamplePath != None:
        # add the samples to samples directory for voice
        copyToSamplesDirectory(voiceName, orgSamplePath, False)
        
def copyToSamplesDirectory(voiceName, orgSamplePath, needNewDirectory):
    """Adds sample files to sample directory to voice in voiceProfile directory
    voiceName: string, name of voice
    orgSamplePath: string, path to where samples are being copied from
    needNewDirectory: bool, true if a new directory is needed"""

    # path for storing samples
    samplePath = voiceProfilePath + f'/{voiceName}/samples'
    
    # copy files to voice samples for storing
    if needNewDirectory:
        try:
            shutil.copytree(orgSamplePath, samplePath)
        except FileExistsError:
            guiFunctions.messageBox("Name already exists.")
            return
    else:
        for sampleName in listdir_nohidden(orgSamplePath):
            copiedSample = orgSamplePath + f'/{sampleName}'
            shutil.copy(copiedSample, samplePath)

# creates list of voice names
# toggle: if true returns voice names in voiceProfiles directory, if false returns voice names uploaded to elevenlabs
def getProfileNames(toggle):
    if toggle:
        voiceNames = listdir_nohidden(voiceProfilePath)
       
    else:
        voiceObjs = main.getUser().get_available_voices()
        voiceNames = []

        # fill list of voice names and voice profiles with only cloned voices
        for voiceObj in voiceObjs:
            if isinstance(voiceObj, ElevenLabsClonedVoice):
                voiceNames.append(voiceObj.get_name())
    
    return voiceNames


def manageScripts():
    # receive script from gui
    guiFunctions.viewAndEditScripts(scriptsPath)

    return
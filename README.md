# elevenlabs-voice-manager

This is a small application designed to make it easier to manage ElevenLabs cloned voices and to get quality audio from them. It does so by giving you a place to manage samples, text files and generated audio. A more in-depth look at what you can do with this application is provided in the usage section.

## Installation

### For Linux
You may need portaudio. On debian and derivatives, you can install with ```sudo apt-get install libportaudio2```, and possibly also  ```sudo apt-get install python3-pyaudio```. The Python 3 and ALSA development packages are required as well, you can use ```sudo apt-get install -y python3-dev libasound2-dev``` to install them. 

### For all platforms
You will need to install ffmpeg, for debian and derivatives use ```sudo apt-get install ffmpeg```.
Use poetry to install the python dependencies, if you don't already have poetry you can install it with ```curl -sSL https://install.python-poetry.org | python3 -```. Run ```poetry install``` on the same level as the pyproject.toml file to install the dependencies.

You will also need an ElevenLabs subscription that has access to instant voice cloning, which is the "Starter" tier and above. Then you will need to get your API key which can be found in your profile settings. You may either set that as an environmental variable named apiKey or simply input it into the prompt when you first launch the application, it will be saved.
	
If you continue to have issues please install soundfile, information on that can be found here: https://github.com/bastibe/python-soundfile#installation. 

## Usage

### Basics
Run with ```poetry run python main.py```. When you first launch the application, it will create two directories, voiceProfiles and scripts, inside your installation directory. Upon creation of each profile, a directory will be created with a matching name inside voiceProfiles. There will be two additional directories inside: one for the samples the voice will use and another to store the generated audio you create from it. If you did not use an environmental variable for your API key, you will be prompted to input it. Once it has registered your API key, you will be on the Profile selection page and have a few options, the ones you will use the most are 'Select profile', 'Create new profile' and 'Manage Scripts'. In this context a profile is simply the samples and generated audio attached to a name.

Please keep in mind that some operations require communication with ElevenLabs, and as such may take longer than expected. On rare occasions an indefinite hang can occur, so if it seems to be taking too long, you may have to close the application.

### Scripts
Before getting into profiles, we will start with scripts. Scripts are just text files used to generate audio. Each text file will be used to generate a single audio file, they cannot be combined, and the text inside will not be split up to create separate audio files. If you have existing text files, you can have the application access them by going to 'Manage Scripts' and then selecting 'Copy from directory'. Make sure that the directory you're copying from does not have anything else inside of it. Inside 'Manage scripts' you can also edit and create text files.

### Profiles
If you're using this for the first time, you will likely have no profiles available and you will just see an empty list. To begin adding profiles, select 'Create new profile'. You will be asked to name the profile. After, you will be asked to select the directory where you have the samples you wish to clone the voice from. Just like with 'Copy from directory' in 'Manage scripts', make sure the directory you select has only the samples in it. Once you submit, an attempt will be made immediately to upload it to ElevenLabs, this may fail depending on if your account already has too many voices. If it does fail, or you provided no samples you can always try again later on that voice's profile page.

### Profile Pages
Profile pages are where you will perform operations with a specific voice. Upon creation of a voice, you will always be brought to that voice's profile page. You can also access a voice profile page by clicking 'Select profile' when you have highlighted a profile on the 'Profile selection' window. There are two versions of the profile page, one where the profile has its samples on ElevenLabs and one where it does not.

When loaded on ElevenLabs, you will have many more options. Most of them are intuitive, but there are some features I'll go into detail about. Firstly, if this is a new profile it won't have any generated audio, so you will want to use the 'Generate and download audio' feature to get started. This will bring up a window with two lists, the one on the right will be all the text files the application can see, and on the left will be the ones that will be used to generate audio files. The left will be empty at first, you can populate it by selecting files on the right and selecting 'Add to upload'. If you wish to remove it after you can select it from either side and click 'Remove from upload'. You can also view and edit the text file from either side with the 'View' button, edits from either side will affect both sides. New text files can be created from there as well. Another important profile page option is 'Manage generated audio', here you can listen to audio that you generated through 'Generate and download audio'. You can also regenerate it if it's not to your liking, and edit the script that it's connected to so that you can regenerate it to say something slightly or even completely different.

When not loaded you will have some of the same options, but any feature related to generating audio will be missing.

Both profile types have ways to swap them in and out of ElevenLabs. When not loaded there is 'Upload profile to ElevenLabs', where you will be able to listen to the samples you have and add new ones. Unlike when you first create the profile, you can select the specific samples you wish to add. When loaded, there is of course an option to remove the profile, but you can also do a reupload. This is basically combining a remove profile operation with an upload, so that you can change which samples are on ElevenLabs. This application currently assumes you can have a max of ten profiles on ElevenLabs, so it will ask you to remove some if you hit that number. This will be changed at some point.

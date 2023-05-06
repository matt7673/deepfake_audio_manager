# deepfake_audio_manager
This is a simple application designed to speed up and simplify the process of producing multiple audio files from a cloned voice. 

## Installation

ElevenLabs and a valid subscription are required for it to work properly. In order to get started you will first have to visit your ElevenLabs account and locate your API key found in your profile settings. For the program to work, this api key is expected to be set as an environmental variable named apiKey. If you do not know about environmental variables, please learn about them here: https://tinyurl.com/env-vars. It is recommended that you make this environmental variable permanent.

You will need to install elevenlabslib which can be done with ```pip install elevenlabslib```. On Linux, you may also need portaudio. On debian and derivatives, you can install with ```sudo apt-get install libportaudio2```, and possibly also  ```sudo apt-get install python3-pyaudio```.
	
If you continue to have issues please install soundfile, information on that can be found here: https://github.com/bastibe/python-soundfile#installation. 

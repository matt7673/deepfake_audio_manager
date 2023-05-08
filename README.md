# deepfake_audio_manager



This is a small application designed to help you manage deepfake voices. It does so by giving you a place to store all of your related deepfake files, such as samples, scripts and generated audio. In addition you can chose which voices should be on ElevenLabs to save space on your account, regenerate audio 

## Installation

A subscription to ElevenLabs is required for it to work properly. In order to get started you will first have to visit your ElevenLabs account and locate your API key found in your profile settings. For the program to work, this api key is expected to be set as an environmental variable named apiKey. If you do not know about environmental variables, please learn about them here: https://tinyurl.com/env-vars. It is recommended that you make this environmental variable permanent.

You will need to install elevenlabslib which can be done with ```pip install elevenlabslib```. On Linux, you may also need portaudio. On debian and derivatives, you can install with ```sudo apt-get install libportaudio2```, and possibly also  ```sudo apt-get install python3-pyaudio```.
	
If you continue to have issues please install soundfile, information on that can be found here: https://github.com/bastibe/python-soundfile#installation. 

## Usage

Once launched, it will ask you for a key if you did not create an environmental variable for it. 

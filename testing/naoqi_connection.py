from naoqi import ALProxy

pepper_ip = "10.0.0.244"
port = 9559

tts = ALProxy("ALTextToSpeech", pepper_ip, port)
tts.say("Hello from my laptop!")

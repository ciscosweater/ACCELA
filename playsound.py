import pygame
import sys
import time

# Takes the full path to a sound file as a command-line argument
sound_file = sys.argv[1]

pygame.mixer.init()
pygame.mixer.music.load(sound_file)
pygame.mixer.music.play()

# Wait for the music to finish playing
while pygame.mixer.music.get_busy():
    time.sleep(0.1)
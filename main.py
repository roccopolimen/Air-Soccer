import pyautogui
from airSoccer import *


# Game Physics Inspired by Peter Colindridge
# http://www.petercollingridge.co.uk/tutorials/pygame-physics-simulation/


if __name__ == '__main__':

	# get the width and height
	width, height = pyautogui.size()
	# width, height = (1920, 900)
	# runs the game
	game = Game(width, height)

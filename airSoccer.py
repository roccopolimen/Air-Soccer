from tkinter import *
from classes import *
import math
import sys


class Game: # Animation Code


	def __init__(self, width, height):

		# Game is ran when a new instance of it is created
		self.run(width, height)


	# How the AI picks a move
	def makeAImove(self, data):

		currentPositions = []
		bestMove = None
		closestDistance = None

		# saves current positions of the balls
		for ball in data.field.getAllBalls():
			currentPositions.append((ball.cx, ball.cy))

		for puck in data.field.getTurnTeam(): # gos through all pucks
			for angle in range(20): # goes through a full rotation
				data.clickedCircle = puck
				data.power = 12
				data.angle = math.pi*angle/10
				self.launch(data) # launches
				data.field.changeTurn()
				data.field.checkCollision(data, True)
				while self.stillMoving(data): # lets the simulation play through
					data.field.checkCollision(data, True)

				# checks if this was a good outcome
				if (closestDistance == None or 
					self.distanceFromGoal(data) < closestDistance):
					closestDistance = self.distanceFromGoal(data)
					bestMove = (puck, 12, angle*math.pi/10)

				# brings the balls back to their original position
				for ballIndex in range(len(data.field.getAllBalls())):
					ball = data.field.getAllBalls()[ballIndex]
					ball.cx, ball.cy = currentPositions[ballIndex]

		# performs the best move found
		data.clickedCircle, data.power, data.angle = bestMove
		self.launch(data)


	# calculates the current distance of the soccer ball from player 1's goal
	def distanceFromGoal(self, data):
		ballX, ballY = (data.field.getAllBalls()[6].cx, 
							data.field.getAllBalls()[6].cy)
		goalX, goalY = (data.width-data.field.width)//2, data.height//2

		return magnitude(ballX, ballY, goalX, goalY)


	# checks if there is any current movement on the field
	def stillMoving(self, data):
		for ball in data.field.getAllBalls():
			if ball.speed != 0:
				return True
		return False


	def launch(self, data): # launch a ball
		for puck in data.field.getTurnTeam():
			if puck == data.clickedCircle:
				puck.speed = data.power
				puck.angle = data.angle
				data.power = None
				data.angle = None
				data.clickedCircle = None
				data.field.changeTurn()
				break


	def play(self, data): # starts the game
		data.State = 'Game'
		data.playBtn = Button()
		data.rulesBtn = Button()
		data.pauseBtn = Button(data.width//2-data.width//20, 
								0, data.width//10, data.height//10, "||", 
								data, self.pauseScreen)


	def displayRules(self, data): # shows the rules screen
		data.State = 'Rules'
		data.playBtn = Button()
		data.rulesBtn = Button()
		data.backBtn = Button(data.width//2-data.width//10, 
								data.height//2+data.height//3, 
								data.width//5, data.height//8, "Back", 
								data, self.goHome)


	def goHome(self, data): # go back to the home screen
		self.init(data)


	def pauseScreen(self, data): # pause the screen
		data.State = "Pause"
		data.backBtn = Button(data.width//2-data.width//10, 
								data.height//2+data.height//3, 
								data.width//5, data.height//8, "Main Menu", 
								data, self.goHome)
		data.playBtn = Button(data.width//2-data.width//10, data.height//2, 
								data.width//5, data.height//8, "Resume", 
								data, self.play)
		data.restartBtn = Button(data.width//2-data.width//10, 
								data.height//2+data.height//6,
								data.width//5, data.height//8, 
								"Restart", 
								data, self.restartGame)
		if data.AI:
			message = "AI: ON"
		else:
			message = "AI: OFF"
		data.aiBtn = Button(data.width//2-data.width//10, 
							data.height//2-data.height//3, 
							data.width//5, data.height//8, 
							message, data, 
							self.switchAI)


	def switchAI(self, data): # Turn on the Game AI
		data.AI = not data.AI
		if data.AI:
			message = "AI: ON"
		else:
			message = "AI: OFF"
		data.aiBtn = Button(data.width//2-data.width//10, 
							data.height//2-data.height//3, 
							data.width//5, data.height//8, 
							message, data, 
							self.switchAI)		


	def restartGame(self, data): # starts the game over
		self.init(data)
		self.play(data)


	def endGame(self, data): # brings up the end screen
		data.State = "End"
		data.backBtn = Button(data.width//2-data.width//10, 
								data.height//2+data.height//3, 
								data.width//5, data.height//8, "Main Menu", 
								data, self.goHome)
		data.restartBtn = Button(data.width//2-data.width//10, 
								data.height//2+data.height//6,
								data.width//5, data.height//8, 
								"Restart", 
								data, self.restartGame)
		data.pauseBtn = Button()


	def init(self, data):
		data.State = 'Home'
		data.AI = False
		data.scoreLimit = 3
		data.field = Field(data.width, data.height, data.scoreLimit)
		data.friction = .005
		data.timeLimit = 6

		# Game variables for launching balls
		data.powerCap = 20
		data.startPower = data.powerCap//2
		data.angleInterval = math.pi/20
		data.clickedCircle = None
		data.power = None
		data.angle = None

		# Button Objects
		data.backBtn = Button()
		data.pauseBtn = Button()
		data.aiBtn = Button()
		data.playBtn = Button(data.width//2-data.width//10, data.height//2, 
								data.width//5, data.height//8, 
								"Play Game", data, self.play)		
		data.rulesBtn = Button(data.width//2-data.width//10, 
								data.height//2+data.height//3, 
								data.width//5, data.height//8, "How To Play", 
								data, self.displayRules)
		data.restartBtn = Button()


	def mousePressed(self, event, data):
		if data.State == 'Home':
			self.homeMousePressed(event, data)
		elif data.State == 'Game':
			self.gameMousePressed(event, data)
		elif data.State == 'Rules':
			self.rulesMousePressed(event, data)
		elif data.State == 'Pause':
			self.pauseMousePressed(event, data)
		elif data.State == 'End':
			self.endMousePressed(event, data)


	def mouseMotion(self, event, data):
		if data.State == 'Game': 
			self.gameMouseMotion(event, data)
		elif data.State == 'Rules':
			self.rulesMouseMotion(event, data)
		elif data.State == 'Home':
			self.homeMouseMotion(event, data)
		elif data.State == 'Pause':
			self.pauseMouseMotion(event, data)
		elif data.State == 'End':
			self.endMouseMotion(event, data)


	def keyPressed(self, event, data):
		if data.State == 'Game':
			self.gameKeyPressed(event, data)


	def timerFired(self, data):
		if data.State == 'Game':
			while self.stillMoving(data):
				data.field.checkCollision(data)
				return
			if data.AI and not data.field.player1_turn:
				self.makeAImove(data)
			if data.field.endGame:
				self.endGame(data)


	def redrawAll(self, canvas, data):
		if data.State == 'Home':
			self.homeRedrawAll(canvas, data)
		elif data.State == 'Game':
			self.gameRedrawAll(canvas, data)
		elif data.State == 'Rules':
			self.rulesRedrawAll(canvas, data)
		elif data.State == 'Pause':
			self.pauseRedrawAll(canvas, data)
		elif data.State == 'End':
			self.endRedrawAll(canvas, data)


	def gameKeyPressed(self, event, data):

		# checks if the user is currently interacting with the circle
		if data.clickedCircle != None:
			if event.keysym == 'space':
				self.launch(data)
			if event.keysym == 'Left' or event.keysym == 'a':
				data.angle -= data.angleInterval
			elif event.keysym == 'Right' or event.keysym == 'd':
				data.angle += data.angleInterval
			elif event.keysym == 'Up' or event.keysym == 'w':
				data.power += 1
				if data.power > data.powerCap:
					data.power = data.powerCap
			elif event.keysym == 'Down' or event.keysym == 's':
				data.power -= 1
				if data.power < 1:
					data.power = 1


	def gameMousePressed(self, event, data):
		data.pauseBtn.clicked(event.x, event.y)
		if data.AI and not data.field.player1_turn: return
		for puck in data.field.getTurnTeam():
			if puck.selected(event.x, event.y):
				data.clickedCircle = puck
				data.angle = math.atan2(data.field.ball.cy-puck.cy, 
					data.field.ball.cx-puck.cx)
				data.power = data.startPower


	def gameMouseMotion(self, event, data):
		data.pauseBtn.hover(event.x, event.y)


	def gameRedrawAll(self, canvas, data):
		data.field.draw(canvas)

		if (data.clickedCircle != None and not
			(not data.field.player1_turn and data.AI)):
			cx, cy = data.clickedCircle.cx, data.clickedCircle.cy
			r = data.clickedCircle.radius*1.1
			canvas.create_oval(cx-r, cy-r, cx+r, cy+r, 
								width=3, outline="yellow")
			endX = cx + (data.power*math.cos(data.angle))*data.power
			endY = cy + (data.power*math.sin(data.angle))*data.power
			canvas.create_line(cx, cy, endX, endY, width=5)
			canvas.create_text(data.width/2, data.height/2+data.height/5, 
								text="Power: "+str(data.power), 
								font="Arial "+str(data.height//25))
		data.pauseBtn.draw(canvas)



	def homeRedrawAll(self, canvas, data):
		canvas.create_rectangle(0, 0, data.width, data.height, fill="green2")
		canvas.create_text(data.width/2, data.height/2-data.height/4, 
						text="Air Soccer", font="Arial "+str(data.height//5))
		data.playBtn.draw(canvas)
		data.rulesBtn.draw(canvas)


	def homeMousePressed(self, event, data):
		data.playBtn.clicked(event.x, event.y)
		data.rulesBtn.clicked(event.x, event.y)


	def homeMouseMotion(self, event, data):
		data.playBtn.hover(event.x, event.y)
		data.rulesBtn.hover(event.x, event.y)


	def rulesRedrawAll(self, canvas, data):

		rulesText = """
		Game Objective
		Use the pucks to collide with the ball and other pucks
		to try and score the ball into the opponents goal
		Game Controls
		If it is your turn, click on one of your pucks
		Use the Up and Down arrow keys to alter power
		Use the left key to rotate aim counter clockwise
		Use the right key to rotate aim clockwise
		click the space bar to send your puck into motion
		Go to the Pause Screen in Game to toggle AI Mode
		**WASD keys also work**"""

		canvas.create_rectangle(0, 0, data.width, data.height, fill="green2")
		data.backBtn.draw(canvas)
		indent = 1
		for line in rulesText.split("\n"):
			line = line.strip()
			canvas.create_text(data.width/10, data.height//18*indent, 
				text=line, font="Arial "+str(data.height//30), anchor="nw")
			indent += 1


	def rulesMousePressed(self, event, data):
		data.backBtn.clicked(event.x, event.y)


	def rulesMouseMotion(self, event, data):
		data.backBtn.hover(event.x, event.y)


	def pauseMousePressed(self, event, data):
		data.playBtn.clicked(event.x, event.y)
		data.backBtn.clicked(event.x, event.y)
		data.restartBtn.clicked(event.x, event.y)
		data.aiBtn.clicked(event.x, event.y)


	def pauseMouseMotion(self, event, data):
		data.playBtn.hover(event.x, event.y)
		data.backBtn.hover(event.x, event.y)
		data.restartBtn.hover(event.x, event.y)
		data.aiBtn.hover(event.x, event.y)


	def pauseRedrawAll(self, canvas, data):
		self.gameRedrawAll(canvas, data)

		canvas.create_text(data.width//2, data.height//10, text="Paused", 
							font="Arial "+str(data.height//20))

		data.playBtn.draw(canvas)
		data.restartBtn.draw(canvas)
		data.backBtn.draw(canvas)
		data.aiBtn.draw(canvas)


	def endMousePressed(self, event, data):
		data.restartBtn.clicked(event.x, event.y)
		data.backBtn.clicked(event.x, event.y)


	def endMouseMotion(self, event, data):
		data.restartBtn.hover(event.x, event.y)
		data.backBtn.hover(event.x, event.y)


	def endRedrawAll(self, canvas, data):
		self.gameRedrawAll(canvas, data)

		canvas.create_text(data.width//2, data.height//10, text="Game Over", 
							font="Arial "+str(data.height//20))

		data.restartBtn.draw(canvas)
		data.backBtn.draw(canvas)

	# contents of run function were received from 15-112 website
	# http://www.cs.cmu.edu/~112n18/notes/notes-animations-demos.html
	# additional code was added by me
	def run(self, width=300, height=300):


	    def redrawAllWrapper(canvas, data):
	        canvas.delete(ALL)
	        canvas.create_rectangle(0, 0, data.width, data.height,
	                                fill='black')
	        self.redrawAll(canvas, data)
	        canvas.update()


	    def mousePressedWrapper(event, canvas, data):
	        self.mousePressed(event, data)
	        redrawAllWrapper(canvas, data)


	    def mouseMotionWrapper(event, canvas, data):
	    	self.mouseMotion(event, data)

	    def keyPressedWrapper(event, canvas, data):
	        self.keyPressed(event, data)
	        redrawAllWrapper(canvas, data)


	    def timerFiredWrapper(canvas, data):
	        self.timerFired(data)
	        redrawAllWrapper(canvas, data)
	        # pause, then call timerFired again
	        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)


	    # closes window when escape key is pressed
	    def close(event):
	    	sys.exit()


	    # Set up data and call init
	    class Struct(object): pass
	    data = Struct()
	    data.width = width*3//4
	    data.height = height*3//4
	    data.timerDelay = 0 # milliseconds
	    root = Tk()

	    # center and fullscreen
	    # root.overrideredirect(1)
	    root.geometry('%dx%d+%d+%d' % (data.width, data.height, 
	    				width//2 - data.width//2, height//2 - data.height//2))
	    self.init(data)

	    # create the root and the canvas
	    canvas = Canvas(root, width=data.width, height=data.height)
	    canvas.pack()

	    # set up events
	    root.bind("<Escape>", close)
	    root.bind("<Button-1>", lambda event:
	                            mousePressedWrapper(event, canvas, data))
	    root.bind("<Key>", lambda event:
	                            keyPressedWrapper(event, canvas, data))
	    root.bind("<Motion>", lambda event:
	    						mouseMotionWrapper(event, canvas, data))
	    timerFiredWrapper(canvas, data)

	    # and launch the app
	    root.mainloop()  # blocks until window is closed


def magnitude(x0, y0, x1=0, y1=0):
	return math.sqrt((x1-x0)**2 + (y1-y0)**2)
import math
import random


class MovingCircle: # represents the balls moving on the screen


	def __init__(self, cx, cy, radius, mass, num):
		self.cx = cx
		self.cy = cy
		self.radius = radius
		self.mass = mass
		self.speed = 0
		self.angle = 0
		self.num = num


	def __repr__(self):
		return ("Num: %d, Speed: %0.001f, angle: %0.001f, mass: %d"%(self.num, 
										self.speed, self.angle, self.mass))


	# moves the circle according to its speed and angle
	def move(self):
		self.cx += self.speed*math.cos(self.angle)
		self.cy += self.speed*math.sin(self.angle)


	# draws the circle to the screen
	def draw(self, canvas, color="blue"):
		cx, cy, r = self.cx, self.cy, self.radius
		canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color)


	# checks if two circles collide
	def collisionWithCircle(self, other):
		if not isinstance(other, MovingCircle): # Avoids Crashing!
			return False

		return( magnitude(self.cx, self.cy, other.cx, other.cy) 
					<= self.radius + other.radius)


	# collides the givne circle with itself
	def collideWithCircle(self, other):

		# ensures there is a collision occuring
		if not self.collisionWithCircle(other): return

		dx = self.cx - other.cx # horizontal distance from the centers
		dy = self.cy - other.cy # vertical distance from the centers

		elasticity = .75 # factor of energy lost in the system
	    
		distance = magnitude(dx, dy)
		angle = math.atan2(dy, dx) # the tangent angle of the colliding circles

		totalMass = self.mass + other.mass

		originalSelfSpeed = self.speed # preserve the value

		# sets the new coordinates based on head to tail addition
		self.angle, self.speed = (makeVector(self.angle, 
			self.speed*(self.mass-other.mass)/totalMass, 
			angle, 2*other.speed*other.mass/totalMass))

		other.angle, other.speed = (makeVector(other.angle, 
			other.speed*(other.mass-self.mass)/totalMass, 
			angle+math.pi, 2*originalSelfSpeed*self.mass/totalMass))

		# account for energy loss
		self.speed *= elasticity
		other.speed *= elasticity

		self.makeTangent(other, angle, distance)


	# removes circle overlap, to avoid infinite collision
	# an issue with computer graphics but not actual physics
	def makeTangent(self, other, angle, distance):

		# calculates the distance the circles overlap
		overlap = (self.radius + other.radius - distance+1)/2

		# moves circles away from each other to avoid remaining overlapped
		self.cx += math.cos(angle)*overlap
		self.cy += math.sin(angle)*overlap
		other.cx -= math.cos(angle)*overlap
		other.cy -= math.sin(angle)*overlap


	# checks if a circle runs into a wall
	def collisionWithWall(self, width, height, margin, goalTop, goalBottom):

		cx, cy, radius = self.cx, self.cy, self.radius

		# hits the top or bottom border
		if cy-radius <= 0 or cy+radius >= height: 
			return True

		# Left and Right Side detection
		if cx-radius <= margin or cx+radius >= margin+width:
			return True

		return False


	# handles the collision between a circle and a wall
	def collideWithWall(self, field, width, height, margin, 
						gTop, gBottom, sim=False):
		elasticity = .75 # energy lost by the system

		# checks if the ball enters the goal
		if isinstance(self, Ball) and not sim:
			if (self.cy-self.radius >= gTop and 
				self.cy+self.radius <= gBottom):

				if self.cx >= width+margin-self.radius: # Right Goal
					field.goalScored(True)

				elif self.cx <= self.radius+margin: # Left Goal
					field.goalScored(False)

		# hits the right wall
		if self.cx > width+margin - self.radius:
		    # self.cx = 2*(width+margin - self.radius) - self.cx
		    self.cx = width+margin-self.radius
		    self.angle = math.pi-self.angle
		    self.speed *= elasticity

		# hits the left wall
		elif self.cx < self.radius+margin:
		    # self.cx = 2*(self.radius+margin) - self.cx
		    self.cx = margin+self.radius
		    self.angle = math.pi-self.angle
		    self.speed *= elasticity

		# hits the bottom wall
		if self.cy > height - self.radius:
		    # self.cy = 2*(height - self.radius) - self.cy
		    self.cy = height-self.radius
		    self.angle = -2*math.pi - self.angle
		    self.speed *= elasticity

		# hits the top wall
		elif self.cy < self.radius:
		    # self.cy = 2*self.radius - self.cy
		    self.cy = self.radius
		    self.angle = 2*math.pi - self.angle
		    self.speed *= elasticity


	# sets the speed of the circle
	def setSpeed(self, speed):
		self.speed = speed
		if self.speed < 0:
			self.speed = 0
			# self.angle = None


	# slows the speed by a frictional coefficient
	def friction(self, mu):
		self.setSpeed(self.speed - mu)


	# checks if the user clicks inside this circle
	def selected(self, mX, mY):
		return magnitude(self.cx, self.cy, mX, mY) <= self.radius


class Ball(MovingCircle): # Soccer Ball, inherited from MovingCircle
	

	def __init__(self, width, height):

		# centers on the screen
		cx = width/2
		cy = height/2
		radius = height//25
		mass = 1
		super().__init__(cx, cy, radius, mass,0)


	def draw(self, canvas):
		super().draw(canvas, "white")


class Field: # The Game Environment where everything happens outside animation


	def __init__(self, width, height, scoreLimit):
		self.width = width*8/10
		self.height = height
		self.margin = (width - self.width) / 2	
		self.goalLength = height/3
		self.ball = Ball(width, height)
		self.player1 = Player("Player 1", width, height, "red")
		self.player2 = Player("Player 2", width, height, "blue", False)
		self.player1_turn = True
		self.scoreLimit = scoreLimit
		self.endGame = False


	# returns a list of all 7 balls that are on the field
	def getAllBalls(self):
		return self.player1.team + self.player2.team + [self.ball]


	# changes who's turn it is
	def changeTurn(self):
		self.player1_turn = not self.player1_turn


	# returns the pucks that are currently active
	def getTurnTeam(self):
		if self.player1_turn:
			return self.player1.team
		return self.player2.team


	def draw(self, canvas):

		# grass of the field
		canvas.create_rectangle(self.margin, 0, self.margin+self.width, 
								self.height, fill="green2")

		# Lines to imitate a soccer field
		canvas.create_line(self.margin + self.width/2, 0, 
							self.margin + self.width/2, 
							self.height/3, fill="white", width=5)
		canvas.create_line(self.margin + self.width/2, self.height*2/3, 
								self.margin + self.width/2, self.height, 
								fill="white", width=5)
		canvas.create_oval(self.margin + self.width/2-self.width/9, 
							self.height/3, 
							self.margin + self.width/2+self.width/9, 
							self.height*2/3, outline="white", width=5)

		self.createGoal(canvas)
		self.ball.draw(canvas)
		self.player1.draw(canvas)
		self.player2.draw(canvas)	
		self.highlightCurrent(canvas)


	# puts a ring around the current team
	def highlightCurrent(self, canvas):
		for puck in self.getTurnTeam():
			r = puck.radius
			canvas.create_oval(puck.cx-r, puck.cy-r, puck.cx+r, puck.cy+r, 
								outline="deep sky blue", width=5)


	def createGoal(self, canvas): # draws the goals
		y0 = self.height/2 - self.goalLength/2
		y1 = y0+self.goalLength

		# Left Goal
		canvas.create_rectangle(0, y0, self.margin, y1, fill="white")

		# Right Goal
		canvas.create_rectangle(self.margin+self.width, y0, 
								self.margin*2+self.width, y1, fill="white")


	# performs all collision functionality, called every timerFired
	def checkCollision(self, data, sim=False):

		for index in range(len(self.getAllBalls())):
			self.getAllBalls()[index].move()

			if (self.getAllBalls()[index].collisionWithWall(self.width, 
											self.height, self.margin, 
											self.height/2-self.goalLength/2, 
											self.height/2+self.goalLength/2)):
				self.getAllBalls()[index].collideWithWall(self, self.width, 
											self.height, self.margin, 
											self.height/2-self.goalLength/2, 
											self.height/2+self.goalLength/2, 
											sim)
			for index2 in range(index+1, len(self.getAllBalls())):
				first = self.getAllBalls()[index]
				other = self.getAllBalls()[index2]
				first.collideWithCircle(other)

			self.getAllBalls()[index].friction(data.friction)


	# updates the game when a goal is scored
	def goalScored(self, rightSide):
		if rightSide:
			self.player1.goals += 1
			self.player1_turn = False
		else:
			self.player2.goals += 1
			self.player1_turn = True
		self.player1.setPucks(True, self.player1.w, 
								self.player1.h)
		self.player2.setPucks(False, self.player2.w, 
								self.player2.h)
		self.ball = Ball(self.width*10/8, self.height)

		if (self.player1.goals == self.scoreLimit or 
			self.player2.goals == self.scoreLimit):
			self.endGame = True


class Puck(MovingCircle): # the Objects that interact on the Field


	def __init__(self, cx, cy, radius, mass, num):
		super().__init__(cx, cy, radius, mass, num)
		self.turn = False


class Player: # The users of each team of pucks
	

	def __init__(self, name, width, height, color, leftSide=True):
		self.name = name
		self.color = color
		self.w, self.h = width, height
		self.setPucks(leftSide, self.w, self.h)
		self.goals = 0
		self.leftSide = leftSide


	def draw(self, canvas):
		for puck in self.team:
			puck.draw(canvas, self.color)
		if self.leftSide:
			canvas.create_text(self.w/20, self.h/12, text="Score", 
								font="Arial "+str(self.h//30), fill=self.color)
			canvas.create_text(self.w/20, self.h/8, text=str(self.goals), 
								font="Arial "+str(self.h//30), fill=self.color)
		else:
			canvas.create_text(self.w*19/20, self.h/12, text="Score", 
								font="Arial "+str(self.h//30), fill=self.color)
			canvas.create_text(self.w*19/20, self.h/8, text=str(self.goals), 
								font="Arial "+str(self.h//30), fill=self.color)


	# initializes pucks to their starting positions
	def setPucks(self, leftSide, w, h):
		if leftSide:
			self.team = [Puck(w/2-w/7, h/2, h/15, random.randint(30, 40), 1), 
							Puck(w/2-w/3.5, h/2-h/4, h//15, random.randint(30, 40), 2), 
							Puck(w/2-w/3.5, h/2+h/4, h//15, random.randint(30, 40), 3)]
		else:
			self.team = [Puck(w/2+w/7, h/2, h/15, random.randint(30, 40), 4), 
							Puck(w/2+w/3.5, h/2-h/4, h//15, random.randint(30, 40), 5), 
							Puck(w/2+w/3.5, h/2+h/4, h//15, random.randint(30, 40), 6)]


class Button: # Basic Button design class
	

	def __init__(self, x=0, y=0, w=0, h=0, text="", data=None, command=None):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.text = text
		self.data = data
		self.command = command
		self.hovered = False


	# called if the button was clicked
	def clicked(self, mX, mY):
		if (mX >= self.x and mX <= self.x + self.w and
			mY >= self.y and mY <= self.y + self.h):
			if self.command != None:
				self.command(self.data)


	# called if the user hovers the mouse over the button
	def hover(self, mX, mY):
		if (mX >= self.x and mX <= self.x + self.w and
			mY >= self.y and mY <= self.y + self.h):
			self.hovered = True
		else:
			self.hovered = False		


	def draw(self, canvas):
		x, y, w, h = self.x, self.y, self.w, self.h
		fontSize = h//4
		if self.hovered:
			color = "red"
		else:
			color = "red4"
		canvas.create_rectangle(x, y, x+w, y+h, fill=color)
		canvas.create_text((x+(x+w))/2, (y+(y+h))/2, text=self.text, 
							fill='black', font="Arial "+str(fontSize))


# finds the distance between the points
def magnitude(x0, y0, x1=0, y1=0):
	return math.sqrt((x1-x0)**2 + (y1-y0)**2)


# Computes head to Tail vector addition
def makeVector(angle1, length1, angle2, length2):
	vx  = math.cos(angle1)*length1 + math.cos(angle2)*length2
	vy  = math.sin(angle1)*length1 + math.sin(angle2)*length2

	angle = math.atan2(vy, vx)
	length  = magnitude(vx, vy)

	return angle, length
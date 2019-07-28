import sys
import math
import pygame
vec = pygame.math.Vector2

# Makes some basic colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
turquoise = (0, 255, 255)
purple = (255, 0, 255)
colors = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'turquoise': (0, 255, 255),
    'purple': (255, 0, 255)
}
# setting the screensize
screen_size = screen_width, screen_height = 900, 600
# making the display
screen = pygame.display.set_mode(screen_size)
# getting the clock object
clock = pygame.time.Clock()
# setting a title to the window
pygame.display.set_caption('Bouncer v1.5')
# getting the font object
pygame.font.init()
text = pygame.font.SysFont('Courier', 20, True)
interface_font = pygame.font.SysFont('Courier', 15, True)

# define essential variables
gravity = vec(0, 100)
overlay = False
fps_limit = 60
run = True


# Class definitions

# ground class
# the angle should be inputted in degrees
class GroundObj:
    def __init__(self, position=vec(int(screen_width // 2), int(screen_height//2)),
                 color=black, width=200, height=100, angle=0):
        self.color = color
        self.position = vec(position)
        self.width = int(width)
        self.height = int(height)
        self.angle = math.radians(angle)

        # Defines the rectangle
        self.ground_rect = pygame.Rect(self.position, (self.width, self.height))

    # The function that draws the rectangle out onto the screen

    def draw(self):
        # Defines the surface upon which the ground rectangle is drawn
        ground_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ground_surface.fill((0, 0, 0, 255))

        # Draws the rect onto the surface
        pygame.draw.rect(ground_surface, black, self.ground_rect)

        # Rotates the surface
        ground_surface = pygame.transform.rotate(ground_surface, math.degrees(self.angle))

        # Sets the surface center equal to the rect's desired center
        self.ground_rect = ground_surface.get_rect(center=self.position)

        # Does the actual drawing
        screen.unlock()
        screen.blit(ground_surface, self.ground_rect)
        if overlay:
            pygame.draw.circle(screen, green, (int(self.position.x), int(self.position.y)), 5)
        screen.lock()


ground_list = [GroundObj((screen_width//2, screen_height//2), black,
                             100, 200, 40)]

# Ball class


class BallObj:
    def __init__(self, position=vec(screen_width/2, screen_height/2-40), r=10, color=blue, width=0,
                 mass=10, velocity=vec(0,0), accel=vec(gravity)):
        # the default ball has a radius of 10 pixels, is blue, is fully colored, starts off still,
        # has a vertical acceleration due to gravity, and starts off at 200, 200
        self.position = vec(position)
        self.r = r
        self.color = color
        self.width = width
        self.mass = mass
        self.velocity = vec(velocity)
        self.accel = vec(accel)
        self.speed = vec.length(self.velocity)

    def draw(self):
        # draws the circle
        int_x, int_y = int(self.position.x), int(self.position.y)
        pygame.draw.circle(screen, self.color, (int_x, int_y), self.r, self.width)

        if overlay:
            # draws a vector line (not to scale)
            x_vel, y_vel = int(self.velocity.x), int(self.velocity.y)
            pygame.draw.line(screen, black, (int_x, int_y), (int_x + x_vel, int_y + y_vel))

    def move(self):
        self.bounce()
        self.position += self.velocity * dtime + 0.5 * (self.accel) * (dtime ** 2)
        self.velocity += self.accel * dtime
        self.accel = gravity

    def bounce(self):
        # collision handling with ground objects
        # REMEMBER TO USE RADIANS
        for ground in ground_list:

            position_diff = self.position - ground.position
            ball_to_rect_center = vec.length(position_diff)

            def get_angle_to_center(pd=position_diff, btrc=ball_to_rect_center):
                if pd.x == 0 and ground.angle == 0:
                    return 0
                elif pd.y == 0 and ground.angle == 0:
                    return math.pi/2
                else:
                    return (-ground.angle + ((math.pi/2) - math.asin(-pd.y/btrc))
                                       * -sign(pd.x))
            angle_to_center = get_angle_to_center()

            def get_vc():
                return ball_to_rect_center * math.cos(angle_to_center)

            def get_hc():
                return ball_to_rect_center * math.sin(-angle_to_center)

            vertical_component = get_vc()
            horizontal_component = get_hc()

            # Overlay code: draws lines and visual representations of distance components
            if overlay:
                pygame.draw.line(screen, turquoise, self.position, ground.position)
                pygame.draw.line(screen, blue, (self.position.x, ground.position.y), ground.position)
                pygame.draw.line(screen, green, self.position, (self.position.x, ground.position.y))

                vert_tri_x = ground.position.x - (vertical_component * math.cos((math.pi/2) - ground.angle))
                vert_tri_y = ground.position.y - (vertical_component * math.sin((math.pi/2) - ground.angle))

                hor_tri_x = ground.position.x + (horizontal_component * math.cos(-ground.angle))
                hor_tri_y = ground.position.y + (horizontal_component * math.sin(-ground.angle))

                pygame.draw.line(screen, red, ground.position, (vert_tri_x, vert_tri_y))
                pygame.draw.line(screen, yellow, ground.position, (hor_tri_x, hor_tri_y))

            vert_reflection_vector = vec(sign(vertical_component) * round(math.sin(ground.angle), 4),
                                                         sign(vertical_component) * round(math.cos(ground.angle), 4))
            hori_reflection_vector = vec(sign(horizontal_component) * round(math.cos(ground.angle), 4),
                                                         sign(horizontal_component) * round(-math.sin(ground.angle), 4))
            # Constants for the rectangle
            corner_angle = math.atan(ground.height / ground.width)
            corner_to_center = (((ground.height // 2)**2) + ((ground.width // 2)**2))**0.5

            v = sign(vertical_component)
            h = sign(horizontal_component)

            # CORNER COLLISIONS
            # checks to see if the ball is in the corner collision zone. Outside of both the vertical
            # and horizontal boundaries yet beneath the minimum collision distance.
            if ground.width // 2 + self.r >= abs(horizontal_component) > ground.width//2 and \
               ground.height // 2 + self.r >= abs(vertical_component) > ground.height//2:
                # Finds the position of the corner
                corner_pos_x = ground.position.x + -h * (corner_to_center * -math.cos(
                    ground.angle + (v * h) * corner_angle))
                corner_pos_y = ground.position.y + ((-v ** 2) * h) * (corner_to_center * math.sin(
                    ground.angle + (v * h) * corner_angle))
                corner_pos = vec(corner_pos_x, corner_pos_y)
                # pygame.draw.circle(screen, yellow, (int(corner_pos_x), int(corner_pos_y)), 5)

                # Defines the position-difference vector between the ball's center and the corner
                ball_to_corner = self.position - corner_pos

                # Finds the reflection vector for a corner collision
                hyp_ball_pos = self.position
                corner_reflection_vector = hyp_ball_pos - corner_pos

                # Checks for a true corner collision (the above conditions are faulty apparently)
                if vec.length(ball_to_corner) < self.r:
                    # Finds where the ball would have been in a pixel-perfect collision along the past trajectory
                    while int(vec.length(corner_reflection_vector)) != self.r:
                        if vec.length(self.velocity) != 0:
                            hyp_ball_pos = hyp_ball_pos - vec.normalize(self.velocity)
                        corner_reflection_vector = hyp_ball_pos - corner_pos
                    # self.position = hyp_ball_pos

                    # rhbpd = Real-Hypothetical Ball Position Difference
                    rhbpd = self.position - hyp_ball_pos
                    rhbpd_length = vec.length(rhbpd)

                    # Calculates the ball's velocity just prior to reflecting velocity in a pixel-perfect scenario
                    prior_v_x = math.sqrt((self.velocity.x**2) - 2*gravity.x*rhbpd.x)
                    prior_v_y = math.sqrt((self.velocity.y**2) - 2*gravity.y*rhbpd.y)
                    prior_v = vec(prior_v_x, prior_v_y)
                    prior_v_length = vec.length(prior_v)

                    # Reflects the ball's velocity about the position-difference vector
                    self.velocity = vec.reflect(self.velocity, corner_reflection_vector)

                    # Calculates the elapsed time from pixel-perfect position to actual current position
                    rhbpd_dt = (2*rhbpd_length)/(self.speed + prior_v_length)

                    # Displaces the ball the appropriate distance along the new velocity vector
                    # s = ut + 0.5*a*t**2
                    initial_v = vec.normalize(self.velocity)*prior_v_length
                    required_displacement_x = (initial_v.x * rhbpd_dt) + (0.5*gravity.x*(rhbpd_dt**2))
                    required_displacement_y = (initial_v.y * rhbpd_dt) + (0.5*gravity.y*(rhbpd_dt**2))
                    required_displacement = vec(required_displacement_x, required_displacement_y)
                    self.position = hyp_ball_pos + required_displacement

            # VERTICAL COLLISIONS
            # checks to see if the ball is in the vertical collision zone. Between the horizontal boundaries,
            # above/below the ground object's top and bottom surfaces, and beneath the minimum collision distance.
            elif ground.height//2 < abs(vertical_component) <= ground.height//2 + self.r:
                if abs(horizontal_component) <= ground.width//2:
                    # Calculates the distance vector that is the difference between the ball's position and the vertical
                    # collision boundary's position
                    dist_to_vert_boundary = (ground.height//2 + self.r) - abs(vertical_component)
                    # vector_dtvb = vec(dist_to_vert_boundary*math.cos(ground.angle),
                    #                                   dist_to_vert_boundary*math.sin(ground.angle))
                    hyp_dtvb = dist_to_vert_boundary
                    hyp_ball_pos = self.position

                    # Finds where the ball would have been in a pixel-perfect collision along the past trajectory
                    if dist_to_vert_boundary < 0:
                        while int(hyp_dtvb) != self.r:
                            if vec.length(self.velocity) != 0:
                                hyp_ball_pos -= vec.normalize(self.velocity)
                                hyp_pd = hyp_ball_pos - ground.position
                                hyp_btrc = vec.length(hyp_pd)
                                hyp_vc = hyp_btrc * math.cos(get_angle_to_center(hyp_pd, hyp_btrc))
                                hyp_dtvb = (ground.height // 2 + self.r) - abs(hyp_vc)

                    # rhbpd = Real-Hypothetical Ball Position Difference
                    rhbpd = self.position - hyp_ball_pos
                    rhbpd_length = vec.length(rhbpd)

                    # Calculates the ball's velocity just prior to reflecting velocity in a pixel-perfect scenario
                    prior_v_x = math.sqrt((self.velocity.x ** 2) - 2 * gravity.x * rhbpd.x)
                    prior_v_y = math.sqrt((self.velocity.y ** 2) - 2 * gravity.y * rhbpd.y)
                    prior_v = vec(prior_v_x, prior_v_y)
                    prior_v_length = vec.length(prior_v)

                    # Reflects the ball's velocity about the position-difference vector
                    self.velocity = vec.reflect(self.velocity, vert_reflection_vector)

                    # Calculates the elapsed time from pixel-perfect position to actual current position
                    rhbpd_dt = (2 * rhbpd_length) / (self.speed + prior_v_length)

                    # Displaces the ball the appropriate distance along the new velocity vector
                    # s = ut + 0.5*a*t**2
                    initial_v = vec.normalize(self.velocity) * prior_v_length
                    required_displacement_x = (initial_v.x * rhbpd_dt) + (0.5 * gravity.x * (rhbpd_dt ** 2))
                    required_displacement_y = (initial_v.y * rhbpd_dt) + (0.5 * gravity.y * (rhbpd_dt ** 2))
                    required_displacement = vec(required_displacement_x, required_displacement_y)
                    self.position = hyp_ball_pos + required_displacement

            # HORIZONTAL COLLISIONS
            # checks to see if the ball is in the horizontal collision zone. Between the vertical boundaries,
            # left/right of the ground object's side surfaces, and beneath the minimum collision distance.
            elif ground.width//2 < abs(horizontal_component) <= ground.width//2 + self.r:
                if abs(vertical_component) <= ground.height//2:

                    dist_to_hor_boundary = (ground.width // 2 + self.r) - abs(horizontal_component)
                    hyp_dthb = dist_to_hor_boundary
                    hyp_ball_pos = self.position

                    # Finds where the ball would have been in a pixel-perfect collision along the past trajectory
                    if dist_to_hor_boundary < 0:
                        while int(hyp_dthb) != self.r:
                            if vec.length(self.velocity) != 0:
                                hyp_ball_pos -= vec.normalize(self.velocity)
                                hyp_pd = hyp_ball_pos - ground.position
                                hyp_btrc = vec.length(hyp_pd)
                                hyp_hc = hyp_btrc * math.cos(get_angle_to_center(hyp_pd, hyp_btrc))
                                hyp_dthb = (ground.height // 2 + self.r) - abs(hyp_hc)

                    # rhbpd = Real-Hypothetical Ball Position Difference
                    rhbpd = self.position - hyp_ball_pos
                    rhbpd_length = vec.length(rhbpd)

                    # Calculates the ball's velocity just prior to reflecting velocity in a pixel-perfect scenario
                    prior_v_x = math.sqrt((self.velocity.x ** 2) - 2 * gravity.x * rhbpd.x)
                    prior_v_y = math.sqrt((self.velocity.y ** 2) - 2 * gravity.y * rhbpd.y)
                    prior_v = vec(prior_v_x, prior_v_y)
                    prior_v_length = vec.length(prior_v)

                    # Reflects the ball's velocity about the position-difference vector
                    self.velocity = vec.reflect(self.velocity, hori_reflection_vector)

                    # Calculates the elapsed time from pixel-perfect position to actual current position
                    try:
                        rhbpd_dt = (2 * rhbpd_length) / (self.speed + prior_v_length)
                    except ZeroDivisionError:
                        rhbpd_dt = 1

                    # Displaces the ball the appropriate distance along the new velocity vector
                    # s = ut + 0.5*a*t**2
                    try:
                        initial_v = vec.normalize(self.velocity) * prior_v_length
                    except ValueError:
                        initial_v = vec(0, 0)
                    required_displacement_x = (initial_v.x * rhbpd_dt) + (0.5 * gravity.x * (rhbpd_dt ** 2))
                    required_displacement_y = (initial_v.y * rhbpd_dt) + (0.5 * gravity.y * (rhbpd_dt ** 2))
                    required_displacement = vec(required_displacement_x, required_displacement_y)
                    self.position = hyp_ball_pos + required_displacement

balls = [BallObj(r=40, position=vec(0, 0))]


class SpawnInterface:
    def __init__(self, position, width, height):
        self.position = vec(position)
        self.width = int(width)
        self.height = int(height)
        self.rectangle = pygame.Rect(position, (width, height))
        self.surface = pygame.Surface((width, height))
        self.buttons = []
        self.texts = []
        self.inputs = []

    def set_buttons(self, buttons_list):
        self.buttons += buttons_list

    def get_buttons(self):
        return self.buttons

    def set_texts(self, texts_list):
        self.texts = texts_list

    def get_texts(self):
        return self.texts

    def set_inputs(self, inputs_list):
        self.inputs = inputs_list

    def get_inputs(self):
        return self.inputs

    def draw(self):
        self.surface.fill((100, 100, 100))
        self.surface.set_alpha(200)
        screen.unlock()
        self.surface.unlock()
        for button in self.buttons:
            button.update()
            button.draw()
            self.surface.blit(button.surface, button.position)
        for te in self.texts:
            te.draw()
            te.surface.unlock()
            self.surface.blit(te.surface, te.position)
        for ib in self.inputs:
            ib.update()
            ib.draw()
            ib.surface.unlock()
            self.surface.blit(ib.surface, ib.position)
        screen.blit(self.surface, self.rectangle)


class InterfaceText:
    def __init__(self, position, interface_text, font=interface_font, h_padding=10, v_padding=5):
        self.position = vec(tuple(position))
        self.interface_text = str(interface_text)
        self.font = font
        self.h_padding = h_padding
        self.v_padding = v_padding
        self.w, self.h = self.font.size(interface_text)
        self.width, self.height = self.w+2*self.h_padding, self.h+2*self.v_padding
        for f in interface_text:
            if f == "\n":
                self.height += self.h
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface.lock()

    def draw(self, text_color=blue):
        self.surface.unlock()
        i_t_strings = self.interface_text.split("\n")
        i = 0
        for i_t in i_t_strings:
            i += 1
            i_t_surface = self.font.render(i_t, True, text_color)
            self.surface.blit(i_t_surface, (self.h_padding, self.v_padding+self.h*(i-1)))


class Button(InterfaceText):
    def __init__(self, position, button_text="hi im a button", rest_color=black,
                 pressed_color=red, border_color=black, is_hovered=False, is_pressed=False):
        super().__init__(position, button_text)
        self.button_text = self.interface_text
        self.rest_color = rest_color
        self.pressed_color = pressed_color
        self.border_color = border_color
        self.is_hovered = bool(is_hovered)
        self.is_pressed = bool(is_pressed)

    def draw(self):
        if self.is_pressed:
            self.surface.fill(self.pressed_color)
        else:
            self.surface.fill(self.rest_color)
        pygame.draw.rect(self.surface, self.border_color, (0, 0, self.width, self.height), 3)
        super().draw()

    def update(self):
        mpx, mpy = pygame.mouse.get_pos()
        # Changes the border color of the button if the mouse is hovering over it
        top_ = spawn_interface.position.y + self.position.y
        left_ = spawn_interface.position.x + self.position.x
        if is_in_rect(mpx, mpy, left_, top_, self.width, self.height) and overlay:
            self.is_hovered = True
        else:
            self.is_hovered = False
        if self.is_hovered:
            self.border_color = yellow
        else:
            self.border_color = black


class InputBox(Button):
    def __init__(self, position, width, prompt="Input Here", background_color=white, border_color=black,
                 is_pressed=False, is_hovered=False):
        InterfaceText.__init__(self, position, prompt)

        if self.width < width:
            self.width = width
        self.h_padding = 5
        self.prompt = str(prompt)
        self.background_color = background_color
        self.border_color = border_color
        self.is_pressed = bool(is_pressed)
        self.is_hovered = bool(is_hovered)
        self.input_text = []
        self.cursor_pos = 0
        self.input_string = ''

    def get_input_string(self):
        string = ''
        for o in self.input_text:
            string += o
        self.input_string = string
        return string

    def draw(self):
        self.surface.fill(self.background_color)
        pygame.draw.rect(self.surface, self.border_color, (0, 0, self.width, self.height), 3)
        self.surface.unlock()
        if self.is_pressed or len(self.input_text) > 0:
            input_surface = interface_font.render(self.get_input_string(), True, black)
        elif (not self.is_pressed) and len(self.input_text) == 0:
            input_surface = interface_font.render(self.prompt, True, black)
        self.surface.blit(input_surface, (self.h_padding, self.v_padding))

    def update(self):
        super().update()

    def user_input(self, e, k):
        # Typing activated
        if e.key != 13 and e.key != 273 and e.key != 274 and e.key != 275 and e.key != 276 and e.key != 127 and \
           e.key != pygame.K_BACKSPACE and e.key != pygame.K_ESCAPE:
            self.input_text.insert(self.cursor_pos, e.unicode)
            self.cursor_pos += 1
        elif e.key == pygame.K_BACKSPACE and self.cursor_pos > 0:
            del self.input_text[self.cursor_pos-1]
            self.cursor_pos -= 1
        elif e.key == pygame.K_RIGHT and self.cursor_pos < len(self.input_text):
            self.cursor_pos += 1
        elif e.key == pygame.K_LEFT and self.cursor_pos > 0:
            self.cursor_pos -= 1
        elif e.key == pygame.K_ESCAPE:
            self.is_pressed = False

# Sets up the ball and ground object spawner interfaces

spawn_interface = SpawnInterface((screen_width - 400, 10), 370, 250)

spawn_interface_title = InterfaceText((0, 0),
                                      "The Spawner\nSelect the object you would like to spawn\nand it's properties, "
                                      "then \nleft click to spawn it.")
ball_texts = [
    InterfaceText((10, spawn_interface_title.height+40),
                  "radius", interface_font),
    InterfaceText((10, spawn_interface_title.height+70),
                  "color", interface_font),
    InterfaceText((10, spawn_interface_title.height+100),
                  "border width", interface_font),
]

ground_texts = [
    InterfaceText((10, spawn_interface_title.height+40),
                  "width", interface_font),
    InterfaceText((10, spawn_interface_title.height+70),
                  "height", interface_font),
    InterfaceText((10, spawn_interface_title.height+100),
                  "angle (degrees)", interface_font),
    InterfaceText((10, spawn_interface_title.height+130),
                  "color", interface_font),
]

ball_inputs = [
    InputBox((160, spawn_interface_title.height+40), 50, "[int or float]"),
    InputBox((160, spawn_interface_title.height + 70), 50, "[color name or rgb]"),
    InputBox((160, spawn_interface_title.height + 100), 50, "[int, 0 means filled]")
]

ground_inputs = [
    InputBox((160, spawn_interface_title.height + 40), 50, "[positive integer plz]"),
    InputBox((160, spawn_interface_title.height + 70), 50, "[also positive int]"),
    InputBox((160, spawn_interface_title.height + 100), 50, "[integer, degrees]"),
    InputBox((160, spawn_interface_title.height + 130), 50, "[name of the color]")
]
spawn_interface.set_inputs(ball_inputs)

spawn_interface.set_texts([spawn_interface_title]+ball_texts)

min_button_height = spawn_interface_title.position[0]+spawn_interface_title.height
ball_button = Button((10, min_button_height+10), "ball", is_pressed=True)
ground_button = Button((20+ball_button.width, min_button_height+10), "rectangle")
spawn_interface.set_buttons([ball_button, ground_button])

# Defining a function that returns whether a number is positive, negative, or zero


def sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    else:
        return 0

# Defines a function that says whether or not a point is within a rectangle


def is_in_rect(x, y, left, top, width, height):
    return left <= x <= left+width and top <= y <= top+height


# Main Loop
while run:

    # Limit the frame-rate
    dtime = (clock.tick(fps_limit)) / 1000

    # Get the list of keys that are and aren't being pressed during this frame
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # Mouse-click events
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
            # LMB event, spawns new ball unless clicking the spawn interface
            if is_in_rect(mouse_pos_x, mouse_pos_y, spawn_interface.position.x, spawn_interface.position.y,
                          spawn_interface.width, spawn_interface.height) and overlay:
                t = ""

                # "bl" stands for "button list"
                # loops through all buttons of the interface, if one is hovered while left clicking, all are set to
                # is_pressed = False and the hovered one gets set to is_pressed = True
                bl = spawn_interface.get_buttons()
                for button in bl:
                    if button.is_hovered:
                        for b in bl:
                            b.is_pressed = False
                        button.is_pressed = True
                if ball_button.is_pressed:
                    spawn_interface.set_texts([spawn_interface_title] + ball_texts)
                    spawn_interface.set_inputs(ball_inputs)
                elif ground_button.is_pressed:
                    spawn_interface.set_texts([spawn_interface_title] + ground_texts)
                    spawn_interface.set_inputs(ground_inputs)
                else:
                    spawn_interface.set_texts([spawn_interface_title])
                    spawn_interface.set_inputs([])

                il = spawn_interface.get_inputs()
                for i in il:
                    if i.is_hovered:
                        for j in il:
                            j.is_pressed = False
                        i.is_pressed = True

            else:
                if pygame.mouse.get_pressed() == (1, 0, 0):
                    if ball_button.is_pressed:
                        try:
                            ball_radius = int(ball_inputs[0].get_input_string())
                        except ValueError:
                            ball_radius = 20

                        if ball_inputs[1].get_input_string() in colors:
                            ball_color = colors[ball_inputs[1].get_input_string()]
                        else:
                            ball_color = blue

                        try:
                            ball_width = int(ball_inputs[2].get_input_string())
                            print(ball_width)
                            if ball_width <= 0:
                                raise ValueError
                        except ValueError:
                            ball_width = 0

                        balls.append(BallObj(position=vec(mouse_pos_x, mouse_pos_y),
                                             velocity=vec(0, 0), r=ball_radius, color=ball_color, width=ball_width))
                    elif ground_button.is_pressed:
                        # width
                        try:
                            ground_width = int(ground_inputs[0].get_input_string())
                            if ground_width < 0:
                                raise ValueError
                        except ValueError:
                            ground_width = 20
                        # height
                        try:
                            ground_height = int(ground_inputs[1].get_input_string())
                            if ground_height < 0:
                                raise ValueError
                        except ValueError:
                            ground_height = 20
                        # angle
                        try:
                            ground_angle = int(ground_inputs[2].get_input_string())
                        except ValueError:
                            ground_angle = 20
                        # color
                        if ground_inputs[3].get_input_string() in colors:
                            ground_color = colors[ground_inputs[3].get_input_string()]
                        else:
                            ground_color = black

                        ground_list.append(GroundObj((mouse_pos_x, mouse_pos_y), ground_color, ground_width, ground_height, ground_angle))

            # RMB event, deletes all balls touching the cursor
            if pygame.mouse.get_pressed() == (0, 0, 1):
                for i, ball in enumerate(balls):
                    mouse_pos = vec(mouse_pos_x, mouse_pos_y)
                    if vec.length(mouse_pos - ball.position) <= ball.r:
                        del(balls[i])

        if keys[pygame.K_f]:
            # Sets the "draw fancy stuff" global variable (overlay) equal to true
            if overlay is True: overlay = False
            elif overlay is False: overlay = True

        for inp in spawn_interface.get_inputs():
            if inp.is_pressed and event.type == pygame.KEYDOWN:
                inp.user_input(event, keys)

        # User-input gravity adjustment
        g_multiplier = 1
        if (keys[pygame.K_UP] ^ keys[pygame.K_DOWN]) or (keys[pygame.K_LEFT] ^ keys[pygame.K_RIGHT]):
            if (pygame.key.get_mods() & pygame.KMOD_LSHIFT) ^ (pygame.key.get_mods() & pygame.KMOD_LCTRL):
                if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                    g_multiplier = 10
                elif pygame.key.get_mods() & pygame.KMOD_LCTRL:
                    g_multiplier = 0.1
                else:
                    g_multiplier = 1
        if keys[pygame.K_g]:
            if keys[pygame.K_UP]:
                gravity += vec(0, (-10*g_multiplier))
            elif keys[pygame.K_DOWN]:
                gravity += vec(0, (10*g_multiplier))
            if keys[pygame.K_LEFT]:
                gravity += vec((-10*g_multiplier), 0)
            elif keys[pygame.K_RIGHT]:
                gravity += vec((10*g_multiplier), 0)

    screen.lock()
    # Draw the background over everything (erase it all)
    screen.fill((120, 120, 120))

    # Doing the rest of the physics, updating, and drawing
    for ground in ground_list:
        ground.draw()

    for i, ball in enumerate(balls):
        ball.draw()
        ball.move()
        # deletes the ball if it falls off of the screen except if it goes up
        if ball.position.y > screen_height + ball.r or ball.position.x < ball.r or ball.position.x > screen_width + ball.r:
            del(balls[i])

    # more overlay text + interface button stuff

    screen.unlock()
    if overlay:
        grav_text = text.render("gravity: " + str(int(gravity.x)) + ", " + str(int(gravity.y)), True, black)
        screen.blit(grav_text, (10, 10))
        spawn_interface.draw()

    pygame.display.flip()

pygame.font.quit()
pygame.quit()
sys.exit()

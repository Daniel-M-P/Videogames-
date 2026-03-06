import pygame
import os
import random
pygame.font.init()

# Constants
COLUMNS = 36
ROWS = 20
OBJECT_WIDTH = 25
OBJECT_HEIGHT = 33
SIZE = WIDTH, HEIGHT = COLUMNS*OBJECT_WIDTH, ROWS*OBJECT_HEIGHT
WIN = pygame.display.set_mode((SIZE))
pygame.display.set_caption("Centipede")

# Load images
# The ones that are lists are the ones with different frames for animation
PLAYER_IMG = pygame.image.load(os.path.join("Assets", "player.png")).convert()
HEADS = [pygame.image.load(os.path.join("Assets", "head0.png")).convert(),
         pygame.image.load(os.path.join("Assets", "head1.png")).convert(),
         pygame.image.load(os.path.join("Assets", "head2.png")).convert()]
SEGMENTS = [pygame.image.load(os.path.join("Assets", "segment0.png")).convert(),
            pygame.image.load(os.path.join("Assets", "segment1.png")).convert(),
            pygame.image.load(os.path.join("Assets", "segment2.png")).convert()]
MUSHROOMS = [pygame.image.load(os.path.join("Assets", "mushroom0.png")).convert(),
            pygame.image.load(os.path.join("Assets", "mushroom1.png")).convert(),
            pygame.image.load(os.path.join("Assets", "mushroom2.png")).convert(),
            pygame.image.load(os.path.join("Assets", "mushroom3.png")).convert()]
SPIDER = pygame.image.load(os.path.join("Assets", "spider0.png")).convert()
SCORPION = pygame.image.load(os.path.join("Assets", "scorpion0.png")).convert()
FLEAS = [pygame.image.load(os.path.join("Assets", "flea0.png")).convert(),
        pygame.image.load(os.path.join("Assets", "flea1.png")).convert()]
LASER = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "laser.png")).convert(), (3,10))
SEGMENTS_ROTATED = [pygame.transform.rotate(segment,180) for segment in SEGMENTS]
HEADS_ROTATED = [pygame.transform.rotate(head,180) for head in HEADS]

class Entity():
    def __init__(self, x, y, img, frames=None):
        self.x = x
        self.y = y
        self.frames = frames
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        self.state = 0

    def draw(self,window):
        window.blit(self.img, (self.x, self.y))

    def get_row(self):     
        return int(self.y // OBJECT_HEIGHT)

    def get_column(self):
        return int(self.x // OBJECT_WIDTH)

    def off_screen_v(self, height):
        return not(self.y <= height and self.y >= 0)

    def off_screen_h(self, width):
        return not(self.x <= width and self.x >= 0)

    def collision(self, obj):
        return collide(self, obj)

        
class Centipede_part(Entity):
    def __init__(self, x, y, direction, vel, body_part, tail_length=0):
        self.body_part = body_part
        self.change_part()

        super().__init__(x, y, self.img, self.frames)
        self.horizontal = 1 # 1 for right, -1 for left
        self.vertical = 1 # 1 for up, -1 for down
        self.vel = 2.5
        self.rotate = True
        self.tail_length = tail_length
        self.goin_up = 0
        self.skip_collision = 0
        self.tail = []

        if tail_length > 0 and self.body_part == "Head":
            for segment in range(tail_length):
                self.tail.insert(0, Centipede_part(self.x - OBJECT_WIDTH*(segment+1), self.y, direction, vel, "Tail", tail_length-segment-1))

    def get_tail_length(self):
        return len(self.tail)

    def get_column(self):
        if self.horizontal == 1:
            return int((self.x + OBJECT_WIDTH) // OBJECT_WIDTH)
        
        else: return int(self.x // OBJECT_WIDTH)
    
    def change_part(self):
        if self.body_part == "Head":
            self.img = HEADS[0]
            self.frames = HEADS
            self.rotated_frames = HEADS_ROTATED

        else:
            self.img = SEGMENTS[0]
            self.frames = SEGMENTS
            self.rotated_frames = SEGMENTS_ROTATED

    def update(self):
        self.state += 0.10
        if self.state >= len(self.frames):
            self.state = 0

        if self.rotate:
            self.img = self.frames[int(self.state)]

        else:
            self.img = self.rotated_frames[int(self.state)]

    def draw(self, window):
        super().draw(window)
        if self.tail_length > 0:
            for segment in self.tail:
                segment.draw(WIN)

    # Return true if the head needs to turn (go down by one and go to the opposite side)
    def turn(self):
        # Check for collision with the right side of the screen
        if self.horizontal == 1 and self.x + self.vel + OBJECT_WIDTH > WIDTH:
            return True

        # Check for collision with left side of the screen
        elif self.horizontal == -1 and self.x - self.vel < 0: 
            return True

        else:
            mushroom = all_mushrooms[self.get_column()][self.get_row()]
            if self.collision(mushroom) and mushroom.show:
                return True
        
        return False

    def move(self):
        if self.turn() and self.skip_collision == 0:
            if self.y + self.vel + OBJECT_HEIGHT > HEIGHT:
                self.goin_up = 1
                self.vertical = -1

            elif self.goin_up == 0:
                self.vertical = 1
            
            elif self.goin_up < 6:
                self.goin_up += 1
            
            else:
                self.goin_up = 0
                self.vertical = 1

            self.make_turn()
            self.skip_collision = 1

        else:
            self.move_horizontally()
            if self.skip_collision < 11 and self.skip_collision != 0: 
                self.skip_collision += 1
            else: 
                self.skip_collision = 0

        if self.tail_length > 0: 
            for segment in self.tail:
                segment.move()
        
        self.update()

    def move_horizontally(self):
        if self.horizontal == 1: self.x += self.vel
        else: self.x -= self.vel
        
    def make_turn(self):
        if self.vertical == 1: self.y += OBJECT_HEIGHT 
        else: self.y -= OBJECT_HEIGHT
        self.horizontal = -self.horizontal
        self.rotate = not self.rotate

    def divide_centipede(self, index):
        new_head = self.tail.pop(index - 1)
        new_head.body_part = "Head"
        new_head.change_part()
        for i in range(index - 2, -1, -1):
            segment = self.tail.pop(i)
            new_head.tail.insert(0, segment)

        for segment in self.tail:
            segment.tail_length -= new_head.tail_length + 2

        self.tail_length -= new_head.tail_length + 1
        return new_head

    def mushroom_convertion(self):
        print("MCa")
        # We need to convert the segment in a mushroom, for that we need to decide where to draw it, we will draw it in the column
        # in which there is more part of the segment, so using the x and the object width we decide which column, for the row is 
        # only divide the y by object_height

        if self.horizontal == 1: # the image goes to the right
            # because is going to the right the x is not the leader visually, meaning well whatever that means
            x = self.x + OBJECT_WIDTH
            # We choose the column in which it is depending on that
            column = self.get_column()
            # If the x is less than the column which it is + the half of the pixels we will draw it in the column before
            # Else we draw the mushroom in that column
            if x < column*OBJECT_WIDTH + OBJECT_WIDTH // 2:
                column -= 1
        
        else: #the image goes to the left
            column = self.get_column()

            if self.x < column*OBJECT_WIDTH - OBJECT_WIDTH // 2:
                column -= 1

        row = self.get_row()
        show_mushrooms.append((column,row))
        all_mushrooms[column][row].show = True
        

    def posioned_movement(self):
        pass


class Player(Entity):
    COOLDOWN = 5

    def __init__(self, x, y, img, lives=3):
        super().__init__(x, y, img)
        self.last_x = None
        self.last_y = None
        self.lives = lives
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Entity(self.x + (PLAYER_IMG.get_width() - LASER.get_width())//2, self.y - LASER.get_height(), LASER)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def move_lasers(self, vel, show_mushrooms, centipedes):
        self.cooldown()
        for laser in self.lasers:
            laser.y -= vel
            remove = False

            if laser.off_screen_v(HEIGHT):
                self.lasers.remove(laser)

            elif mushroom_collision(laser):
                # Detect Mushroom collision
                mushroom = mushroom_collision(laser) 
                if mushroom:
                    if mushroom.out_of_frames():
                        mushroom.show = False
                        show_mushrooms.remove((mushroom.column, mushroom.row))
                    else:
                        mushroom.update()
                remove = True
                
            else:
                # Detect Centipedes Collision
                for centipede in centipedes:
                    if laser.collision(centipede):
                        centipede.mushroom_convertion()
                        if centipede.tail:
                            centipedes.append(centipede.divide_centipede(centipede.tail_length))
                        centipedes.remove(centipede)
                        remove = True
                        break

                    else:
                        flag = False
                        for segment in centipede.tail:
                            if laser.collision(segment):
                                segment.mushroom_convertion()
                                if segment.tail_length > 0:
                                    centipedes.append(centipede.divide_centipede(segment.tail_length))

                                else:
                                    for segment in centipede.tail:
                                        segment.tail_length -= 1

                                try:
                                    centipede.tail[segment.tail_length+1].skip_collision = 1
                                except IndexError:
                                    centipede.skip_collision = 1
                                centipede.tail_length -= 1
                                centipede.tail.remove(segment)
                                remove = flag = True
                                break

                        if flag: break

            if laser in self.lasers and remove:
                self.lasers.remove(laser)
    
class Mushroom(Entity):
    def __init__(self, x, y, column, row):
        super().__init__(x, y, MUSHROOMS[0], MUSHROOMS)
        self.show = False
        self.column = column
        self.row = row
    
    def update(self):
        self.state += 1
        self.img = self.frames[self.state]

    def out_of_frames(self):
        if self.state + 1 == len(self.frames):
            return True
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
 

def collide(obj1, obj2):
    offset_x = int(obj2.x - obj1.x)
    offset_y = int(obj2.y - obj1.y)
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def mushroom_collision(obj):
    obj_column = obj.get_column()
    obj_row = obj.get_row() 
    for column in range(obj_column-1, obj_column+2):
        for row in range(obj_row-1, obj_row+2):
            try:
                mushroom = all_mushrooms[column][row]
                if obj.collision(mushroom) and mushroom.show:
                    return mushroom
            except IndexError:
                pass
    return False
    

def initial_mushrooms():
    mushrooms_group = []
    # n = 50%-55% from the total amount of number to choose (COLUMNS)
    reduce_amount = COLUMNS - random.randint(0,4)
    #Create a list of n numbers choosing from a range of (0, COLUMNS), this will be all the x values
    selected_COLUMNS = random.sample(range(COLUMNS), k=reduce_amount//2)

    for select_x in selected_COLUMNS:
        #Choose some amount of rows for each column(x_value)
        amount_rows = random.sample(range(1, ROWS-5), k=random.randint(1,4))
        for select_y in amount_rows:
            mushrooms_group.append((select_x, select_y))
            all_mushrooms[select_x][select_y].show = True
    return mushrooms_group

# Globals
centipedes = [Centipede_part(x=0, y=(ROWS-20)*OBJECT_HEIGHT, direction=1, vel=3, body_part="Head", tail_length=10)]
all_mushrooms = [[Mushroom(column * OBJECT_WIDTH, row * OBJECT_HEIGHT, column, row) for row in range(ROWS)] for column in range(COLUMNS)]
show_mushrooms = []#initial_mushrooms()


def main():
    run = True
    FPS = 60
    clock = pygame.time.Clock()

    d = (COLUMNS-1)*OBJECT_WIDTH

    player = Player(0, 600, PLAYER_IMG)
    player_vel = 6

    background = pygame.Surface(WIN.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    def redraw_window():
        WIN.blit(background, (0, 0))

        if mushroom_collision(player):
            player.x = player.last_x
            player.y = player.last_y            

        player.move_lasers(10, show_mushrooms, centipedes)
        player.draw(WIN)

        for centipede in centipedes:
            centipede.draw(WIN)
            centipede.move()

        for coordinates in show_mushrooms:
            all_mushrooms[coordinates[0]][coordinates[1]].draw(WIN)

        pygame.display.update()

    while run:
        clock.tick(FPS)
        if not centipedes:
            centipedes.append(Centipede_part(x=0, y=(ROWS-10)*OBJECT_HEIGHT, direction=1, vel=3, body_part="Head", tail_length=10))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.last_x = player.x
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + OBJECT_WIDTH < WIDTH: # right
            player.last_x = player.x
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel : # up
            player.last_y = player.y
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + OBJECT_HEIGHT < HEIGHT: # down
            player.last_y = player.y
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        

        redraw_window()

if __name__ == '__main__':
    main()
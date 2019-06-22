## in line 28, self.port should be same as in server.py file. It need be changed every time you play this game.
# Actually this should be a command line arg, which needs 3,4 lines of code; Will you add those lines?

# SNAKES GAME
## every client has a copy of this file. Server.py stores heads coordinates separately as well. 
import socket
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
from random import randint
import ast
from ast import literal_eval as remove_quotes
import time
# from network import Network # class (client.py/network.py)

curses.initscr()
win = curses.newwin(20, 60, 0, 0)
win.keypad(1)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(1)

class Network:
    def __init__(self):
        # print('at start')
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = 'localhost' 
        self.port = 5458
        # print('here')        
        self.addr = (self.host, self.port)
        self.id, self.initial_heads, self.food = self.connect() ## ids given by server. 
        self.num_of_connected_clients = 2

    def connect(self):
        self.client.connect(self.addr)
        id_heads_food = self.client.recv(2048).decode()
        id_assigned_by_server, initial_heads, food = remove_quotes(id_heads_food)
        return id_assigned_by_server, initial_heads, food # get id from server

    def send(self, data):
        """
        :param data: str
        :return: str
        """
        try:

            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)
        

class Snakes(object):
    """docstring for snake"""
    def __init__(self):
        # print('instantiating net')
        self.net = Network() ## net.id has id of this client given by server (i.e. key of this_snake in snakes dict)
        # print('instantiatED net')
        self.snakes = {}
  
    def create_snakes_from_heads(self):
        for _id, head in self.net.initial_heads.items():
            first_cord_of_head = head[0][0]
            second_cord_of_head = head[0][1]
            snake_without_head = [[first_cord_of_head, second_cord_of_head - 1],\
                                  [first_cord_of_head, second_cord_of_head - 2]]
            snake = head + snake_without_head
            self.snakes[_id] = snake

    def update_snakes_heads(self, all_snakes_new_heads):
        for snake_id, head_in_list in all_snakes_new_heads.items():
            new_head = head_in_list[0]
            self.snakes[snake_id][0] = new_head
            
    def update_other_snakes(self, all_snakes_new_heads):
        for snake_id, head_in_list in all_snakes_new_heads.items():
            if snake_id != self.net.id: # this snake already updated. 
                new_head = head_in_list[0]
                self.snakes[snake_id].insert(0, new_head)
#                 self.snakes[snake_id].pop() 
    
    def get_this_snake(self): # snake of this client
        snake_id = int(self.net.id)
        return self.snakes[snake_id], snake_id
        
            
key = KEY_RIGHT 
s = Snakes()

s.create_snakes_from_heads()
# print('all snakes', s.snakes)
food = s.net.food # First food co-ordinates sent by server 

win.addch(food[0], food[1], '*') # Prints the food

while True:     
    if key == 27: # if Esc key is pressed
        break
        
    win.border(0)
    this_snake, this_snake_id = s.get_this_snake()
    # time.sleep(2)
    win.timeout(int(1000 - (len(this_snake)/5 + len(this_snake)/10)%1000))
    prevKey = key   # Previous key pressed
    event = win.getch()

    key = key if event == -1 else event 
    if key not in [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, 27]: # If an invalid key is pressed
        key = prevKey
        
    # new coordinates of this snake's head
    ## do this for all snakes. 
#     print((this_snake))
    this_snake.insert(0, [this_snake[0][0] + (key == KEY_DOWN \
                            and 1) + (key == KEY_UP and -1), \
                              this_snake[0][1] + (key == KEY_LEFT and -1) \
                                  + (key == KEY_RIGHT and 1)])
    
#     print((this_snake))



    this_snake_head = ([this_snake[0][0], this_snake[0][1]])
    id_and_this_snake_head = str((this_snake_id, this_snake_head))
   
    # *********** SENDING TO SERVER   *********** #
    all_snakes_heads_food = s.net.send(id_and_this_snake_head)
    all_snakes_heads, food = remove_quotes(all_snakes_heads_food)
    
    s.update_snakes_heads(all_snakes_heads)
    s.update_other_snakes(all_snakes_heads)



    # Exit if snake crosses the boundaries
    if this_snake[0][0] == 0 or \
        this_snake[0][0] == 19 or this_snake[0][1] == 0 \
            or this_snake[0][1] == 59: break

    # # If snake runs over itself, remove that client's snake
    # if this_snake[0] in this_snake[1:]: break

    # if head of snake 1 collides with any part
    for _id, snake in s.snakes.items():
        if _id != s.net.id:
            if this_snake[0] in snake:
                key = 27
                break
    if key == 27: # if Esc key is pressed, addch spacesn
        break

    # if head of snake 1 collides with any part
    # of other snake: Send None to server. Server
    # will disconnect
    # if heads of two snakes collide, disconnect both.
    #Send None to server. Server will disconnect
    
    if this_snake[0] == food: # When snake eats the food
        ### ************************* FOOD BUG ************************* ###
        ## In the next code line (line 167), server is asked to give food; But unluckily instead of waiting for server's response
        ## it goes to next line. Compare it with line 129, where it moves to next line, once reponse from server is 
        ## received.
        ### ************************* FOOD BUG ************************* ###

        food = s.net.send('No food')
        print('food:', food)
        food = remove_quotes(food)
        win.addch(food[0], food[1], '*')
    else:    
        ## prev tails vanish of all snakes. 
        for _, snake in s.snakes.items():  ## you're popping last elm of every snake
            tail = snake.pop() # prev tail vanishes coupled with new head appears in next line i.e. snake appears to move fwd
            # print('tail to vanish:', tail[0], tail[1])
            win.addch(tail[0], tail[1], ' ')

    # show all snakes 
    # print(s.snakes)
    for _, snake in s.snakes.items():
#         print('a snake: ', snake)
#         print('snake head to put at:', snake[0][0], snake[0][1])
        win.addch(snake[0][0], snake[0][1], '$')
    

curses.endwin()








import socket
from _thread import *
import sys
import ast
from random import randint
from ast import literal_eval as remove_quotes


class SetStage:
    def __init__(self):
        self.snake_heads = {} ## {id: [[x,y]]}
        self.currentId = 0
        self.num_of_players = 2 # sys arg 
        self.food = []
        
    def generate_random_head(self):
        snake_hor_cord = randint(2, 18)
        snake_vert_cord = randint(4, 58)
        snake = [[snake_hor_cord, snake_vert_cord]]
        return snake 

    def set_heads(self):
        for i in range(self.num_of_players):
            self.snake_heads[i] = self.generate_random_head()
    
    def set_food(self):
        while True:
            random_food = [randint(1, 18), randint(1, 58)]
            if self.is_food_valid(random_food):
                self.food = [randint(1, 18), randint(1, 58)]
                break
                
    ## modification: if food in snake- in first line of loop
    def is_food_valid(self, food):
        for _id, snake_head in self.snake_heads.items():
            if food == snake_head[0]:
                return False
        return True
            
            
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server = 'localhost'
port = PORT

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

    
stage = SetStage()
stage.set_heads()
stage.set_food()

s.listen(stage.num_of_players)
print("Waiting for a connection")

initial_heads, food = stage.snake_heads, stage.food

def threaded_client(conn):
#     global currentId,  , food
    conn.sendall(str.encode(str((stage.currentId, stage.snake_heads, stage.food))))
    stage.currentId = stage.currentId + 1
    reply = ''
    while True:
        try:
            data = conn.recv(2048*2)
            
            reply = data.decode('utf-8')
            if reply == 'No food': print('>>>>>>> reply:', reply)
            if not data:
                print('breaking this cleint thread, no data')
                conn.send(str.encode("Disconnected"))
                break
                            
            else:
                if reply == 'No food':
                    print('handling food', self.food)
                    stage.set_food()
                    print('>>>>>>> req recvd for food', str(self.food))
                    reply = str(tuple(self.food))

                else:
                    id_snakeHead = reply
                    print("Recieved: " + id_snakeHead)
                    _id, snake_head = remove_quotes(id_snakeHead)
#                     print('before:', stage.snake_heads)
                    stage.snake_heads[_id] = [snake_head]
#                     print('after:', stage.snake_heads)
                    food = stage.food ## think about it
                    reply = str((stage.snake_heads, food)) ## think about it
                    print("Sending: " + reply)

                conn.sendall(str.encode(reply)) # reply is either
                                                # food or (heads,food)
        except:
            break

    print("Connection Closed")
    conn.close()

while True:
    global num_of_connected_clients
    conn, addr = s.accept()
    num_of_connected_clients = num_of_connected_clients + 1
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))


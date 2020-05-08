import pygame
from pygame.locals import *
import sys
import json
import threading
from chat_utils import *

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREY = (92, 92, 92)




class App:
    def __init__(self,s=None, me='', peer=''):
        self._running = True
        self.screen = None
        self.size = self.weight, self.height = 640, 400
        #---------
        self.s = s
        self.me = me
        self.peer = peer
        
        self.lock = threading.Lock()

        self.receive_thread = threading.Thread(target=self.get_msg)
        self.receive_thread.daemon = True
        
        self.looping_thread = threading.Thread(target=self.running)
        self.looping_thread.daemon = True
        #---------------
        self.POS_moving = False
        self.position = (0,0)
        # self.clock = pygame.time.Clock()

 
    def on_init(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.screen.fill(GREY)
        self._running = True
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            #--------
            mysend(self.s, json.dumps({"action":"quit_game"}))
            #--------
            self._running = False

        elif event.type == pygame.KEYDOWN:
            #press q to quit
            if event.key == pygame.K_q:
                #--------
                mysend(self.s, json.dumps({"action":"quit_game"}))
                #--------
                self._running = False
        
        #mouse down

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.POS_moving = True

        #mouse up
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.POS_moving = False
            

    def get_msg(self):
        # self.lock.acquire()
        try:
            while self.running:
                peer_msg = myrecv(self.s)
                if len(peer_msg) > 0:
                    peer_msg = json.loads(peer_msg)
                    if peer_msg["action"] == "quit_game":
                        self._running = False
                    elif peer_msg["action"] == "new_pos":
                        self.position = peer_msg["position"]
        except:
            print("not Recieving!")
        # finally:
        #     self.lock.release()
    def on_loop(self):
        if self.POS_moving:
            self.position = pygame.mouse.get_pos()
            mysend(self.s, json.dumps({"action":"new_pos", "position":self.position}))
    
    def on_render(self):
        pygame.draw.circle(self.screen, GREEN, self.position, 25, 1)
        pygame.draw.circle(self.screen, BLUE, self.position, 75, 1)
        pygame.draw.circle(self.screen, RED, self.position, 125, 1)
        pygame.display.flip()
        # self.clock.tick(60)

    def on_cleanup(self):
        # self.looping_thread.join(5)
        # self.receive_thread.join(5)
        pygame.quit()

 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        # start two seperate thread, one for recieving message, one for game loop

        self.receive_thread.start()
        self.looping_thread.start()

        self.running()

        self.on_cleanup()

    def running(self):
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()

 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()


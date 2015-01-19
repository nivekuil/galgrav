from __future__ import division

#Neccesary for building the exe
import pygame._view

import pygame
import sys
import math

import events as ev

from random import randint
from pygame.sprite import collide_circle

from twisted.spread import pb        

from main import (EventManager, Model, Planet, Projectile, Player, SimpleAI,
                  find_distance)


import network


class NoTickEventManager(EventManager):
    #Consumes the queue instantly
    def __init__(self):
        EventManager.__init__(self)
        self._lock = False
    def post(self, event):
        self.event_queue.append(event)
        if not self._lock:
            self._lock = True
            self.pump()
            self._lock = False

        
class TextLogView:
    def __init__(self, evm):
        self.evm = evm
        self.evm.register(self)
        
    def notify(self, evt):
        if evt.id == 'PlanetCreated':
            print "Planet Created at %s %s" % evt.model.pos
        elif evt.id == 'ProjectileCreated':
            print "Projectile Created at %s %s" % evt.model.pos
        elif evt.id == 'UpdatePlanetColor':
            print "Planet Color Changed to %s %s %s" % evt.model.owner.color

            
class NetworkClientController(pb.Root):
    def __init__(self, evm):
        self.evm = evm
        self.evm.register(self)

    def remote_StartGame(self):
        self.evm.post( ev.StartGame())
        return 1

    def notify(self, event):
        pass
    
class NetworkClientView(object):
	"""We SEND events to the CLIENT through this object"""
	def __init__(self, evm):
		self.evm = evm
		self.evm.register( self )

		self.clients = []


	#----------------------------------------------------------------------
	def notify(self, evt):
		if evt.id == 'ClientConnect':
			self.clients.append( event.client )


		#don't broadcast events that aren't Copyable
		if not isinstance( evt, pb.Copyable ):
			evName = evt.__class__.__name__
			copyableClsName = "Copyable"+evName
			if not hasattr( network, copyableClsName ):
				return
			copyableClass = getattr( network, copyableClsName )
			evt = copyableClass( evt, sharedObjectRegistry )

		if evt.__class__ not in network.stc:
			#print "SERVER NOT SENDING: " +str(ev)
			return

		#NOTE: this is very "chatty".  We could restrict 
		#      the number of clients notified in the future
		for client in self.clients:
			print "=====server sending: ", str(evt)
			remoteCall = client.callRemote("ServerEvent", evt)

def program_quit():
    pygame.quit()
    sys.exit()

def main():
    global evm, sharedObjectRegistry
    sharedObjectRegistry = {}

    evm = NoTickEventManager()
    clientController = NetworkClientController(evm)
    clientView = NetworkClientView(evm)
    
    log = TextLogView(evm)
    model = Model(evm)
    
    from twisted.internet import reactor
    
    reactor.listenTCP( 8000, pb.PBServerFactory(clientController))

    print 'Starting server..'
    reactor.run()
    
if __name__ == '__main__':
    main()

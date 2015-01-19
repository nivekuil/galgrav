from main import (EventManager, Model, View, Controller)

from twisted.spread import pb
from twisted.internet.selectreactor import SelectReactor
from twisted.internet.main import installReactor

import events as ev

SERVERHOST, SERVERPORT = 'localhost', 8000

class NetworkServerView(pb.Root):
    """We SEND events to the server through this object"""
    STATE_PREPARING = 0
    STATE_CONNECTING = 1
    STATE_CONNECTED = 2

    def __init__(self, evm, shared_obj_registry):
        self.evm = evm
        self.evm.register(self)

        self.pbClientFactory = pb.PBClientFactory()
        
        self.reactor = None
        self.server = None

        self.shared_objs = shared_obj_registry
        self.state = NetworkServerView.STATE_PREPARING
 
    def connected(self, server):
        print 'Connection to %s %s successful' %SERVERHOST, SERVERPORT

        self.state = NetworkServerView.STATE_CONNECTED
        
        self.server = server
        self.evm.post(ev.ServerConnected(server))
        
    def connection_failed(self, error):
        print "Connection failed with error ", error

    def attempt_connection(self):
        print "Attempting connection to", SERVERHOST, SERVERPORT
        
        self.state = NetworkServerView.STATE_CONNECTING
        
        if self.reactor:
            self.reactor.stop()
            self.pump_reactor()
        else:
            self.reactor = SelectReactor()
            installReactor(self.reactor)
        
        connection = self.reactor.connectTCP(SERVERHOST, SERVERPORT,
                                             self.pbClientFactory)
        deferred = self.pbClientFactory.getRootObject()        
        deferred.addCallback(self.connected)
        deferred.addErrback(self.connection_failed)
        self.reactor.run()
        
    def pump_reactor(self):
        self.reactor.runUntilCurrent()
        self.reactor.doIteration(0)

        
    def disconnect(self):
        print "disconnecting"

    def notify(self, evt):
        if evt.id == 'Tick':
            if self.state == NetworkServerView.STATE_PREPARING:
                self.attempt_connection()
            elif self.state in [NetworkServerView.STATE_CONNECTING]:
                self.pump_reactor()
            
class NetworkServerController(pb.Referenceable):
        """We RECEIVE events from the server through this object"""
        def __init__(self, evm):
                self.evm = evm
                self.evm.register( self )

        #----------------------------------------------------------------------
        def remote_ServerEvent(self, evt):
            self.evm.post(evt)
            return 1

        #----------------------------------------------------------------------
        def notify(self, evt):
            if evt.id == 'ServerConnect':
                #tell the server that we're listening to it and
                #it can access this object
                evt.server.callRemote("ClientConnect", self)

def main():
    evm = EventManager()
    shared_obj_registry = {}

    controller = Controller( evm )
    model = Model(evm)
    view = View(evm)


    serverController = NetworkServerController( evm )
    serverView = NetworkServerView( evm, shared_obj_registry )
    
    try:
        controller.tick()
    except Exception, ex:
        print 'got exception (%s)' % ex, 'killing reactor'
        import logging
        logging.basicConfig()
        logging.exception(ex)
        serverView.disconnect()


if __name__ == "__main__":
    main()

import events as ev
import requests as rq
from twisted.spread import pb
#Client-to-server, server-to-client
cts = []
stc = []

def MixInClass( origClass, addClass ):
	if addClass not in origClass.__bases__:
		origClass.__bases__ += (addClass,)

#------------------------------------------------------------------------------
def MixInCopyClasses( someClass ):
	MixInClass( someClass, pb.Copyable )
	MixInClass( someClass, pb.RemoteCopy )


MixInCopyClasses(rq.CreatePlanet)
pb.setUnjellyableForClass(rq.CreatePlanet, rq.CreatePlanet)
cts.append(rq.CreatePlanet)

class CopyableCreatePlanet(pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "CopyableCreatePlanet"
		self.gameID = id(event.game)
		registry[self.gameID] = event.game

pb.setUnjellyableForClass(CopyableCreatePlanet, CopyableCreatePlanet)
stc.append( CopyableCreatePlanet )

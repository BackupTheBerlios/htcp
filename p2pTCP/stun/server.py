from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from p2pnetwork.stun.stun import StunServer


import struct, socket, time, logging

stun = StunServer()

class MessageReceived(StunServer):

    def __init__(self):
        pass
        
reactor.listenUDP(3478, MessageReceived())
reactor.listenUDP(3479, MessageReceived())
reactor.run()

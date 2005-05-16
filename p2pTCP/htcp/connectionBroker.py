from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from p2pnetwork.htcp.punchProtocol import ConnectionBroker
#from p2pnetwork.util.logger import MessageLogger


import struct, socket, time, logging

class MessageReceived(ConnectionBroker):
    
    def __init__(self):
        pass
        
reactor.listenUDP(6060, MessageReceived())
reactor.run()

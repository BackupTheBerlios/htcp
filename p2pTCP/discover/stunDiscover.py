# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>

import os
import twisted.internet.defer as defer
from twisted.python import log, failure

import p2pnetwork.stun.stun as stun
import p2pnetwork.CNProtocol as cnProtocol

stun_section = {
    'servers': ('stun_servers', str, ""),
}

transport = None

#class _StunDiscovery(cnProtocol.CNProtocol):
class _StunDiscovery(stun.StunClient):

    
    def __init__(self, servers = ''): #, *args, **kargs):
        super(_StunDiscovery, self).__init__()
        self.servers = servers

    def Start(self, myPort, reactor, deferred):
        """
        Start listening for STUN replies.
        """

        self.listening = reactor.listenUDP(myPort, self)
        self.myPort = myPort
        # Pass all the variables to the Protocol implemetation
        #self.setDeferred(deferred)
        #self.setTransport(self.transport)
        #self.setListenPort(myPort)
        self.listenPort = myPort
        self.deferred = deferred
        
        # Try to contact the STUN servers 
        for host, port in self.servers:
            def _resolved(host, port):
                self.sendRequest((host, port))
            def _unresolved(failure):
                print failure.getErrorMessage()
            d = reactor.resolve(host)
            d.addCallback(_resolved, port)
            d.addErrback(_unresolved)

    def Stop(self):
        """
        Stop listening.
        """
        
        self.listening.stopListening()
        self.listening = None
        #TODO: alive

    def gotMappedAddress(self, addr = '', port = 0):
        """
        Called back when STUN discovered our public address.
        """
        if not self.deferred.called:
            self.deferred.callback((addr, int(port)))

    def record(self, config):
        """Registration in the rendezvous server"""
        self.publicAddr = config[1]
        self.privateAddr = config[2]
        self.registration(('', self.publicAddr, self.privateAddr, ''))
        
    def connectionMade(self, addr = '', port = 0):
        """
        Called back when STUN discovered our public address.
        """
        if not self.deferred.called:
            print "Connection made!!!!!!!"
            #self.deferred.callback((addr, int(port)))

 
def DiscoverAddress(port, reactor):
    d = defer.Deferred()
    #params.LoadSection('stun', stun_section)
    #servers = params.stun_servers or '127.0.0.1'
    # TODO: read server list from file
    servers = 'localhost'
    serv_list = [(s.strip(), 3478) for s in servers.split(',')]
    discovery = _StunDiscovery(servers=serv_list)
    # Define timeout callback
    def _timeout():
        print 'timeout'
        discovery.Stop()
        d.errback(Exception("timed out with servers %s" % servers))
    # Define intermediary succeed callback
    def _succeed(value):
        # Don't stop: continue to listen on the same port
        discovery.Stop()
        # Registration to the rendezvous server
##         netconf = discovery.getConfiguration()
##         if netconf[0] == 'Yes':
##             discovery.setServer(('127.0.0.1', 6060))
##             discovery.record(('', netconf[2], netconf[3], ''))
        return value
    def _fail(failure):
        print "Discovery result:", failure.getErrorMessage()
        d.errback(failure)
        return failure

    d.addCallback(_succeed)
    d.addErrback(_fail)
    # Start listening
    discovery.Start(port, reactor, d)
    return d

# --------------------------------------------------------------

def printConfiguration():
    """Prints the peer's network configuration"""
    discovery = _StunDiscovery()
    discovery.printConfiguration()

def getConfiguration():
    """Gets a list with the network configuration:
    (NAT presence, NAT type, private address, public address)"""
    discovery = _StunDiscovery()
    return discovery.getConfiguration()

def getNATType():
    """Returns the NAT's type"""
    discovery = _StunDiscovery()
    return discovery.getNATType()

def getPrivateAddress():
    """Retruns the client's private address"""
    discovery = _StunDiscovery()
    return discovery.getPrivateAddress()

def getPublicAddress():
    """Retruns the client's public address"""
    discovery = _StunDiscovery()
    return discovery.getPublicAddress()


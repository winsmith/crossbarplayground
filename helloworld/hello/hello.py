###############################################################################
#
# Copyright (C) 2014, Tavendo GmbH and/or collaborators. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###############################################################################
from random import randrange, choice

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
import redis


registeredDeviceIDs = "registeredDeviceIDs"
notifiedDeviceIDs = "notifiedDeviceIDs"
pin_queue = "pin_queue"

r = redis.StrictRedis(host='localhost', port=6379, db=0)

r.delete(registeredDeviceIDs)
r.delete(notifiedDeviceIDs)

class AppSession(ApplicationSession):

    log = Logger()

    @inlineCallbacks
    def onJoin(self, details):

        # SUBSCRIBE to a topic and receive events
        #
        def onhello(msg):
            self.log.info("event for 'onhello' received: {msg}", msg=msg)

        yield self.subscribe(onhello, 'com.example.onhello')
        self.log.info("subscribed to topic 'onhello'")

        # REGISTER a procedure for remote calling
        #
        def pinUpdated(deviceID, pin, value):
            r.rpush(pin_queue, [deviceID, pin, value])
            self.log.info("Device {deviceID}: pin {x} was updated to {y}",deviceID=deviceID, x=pin, y=value)
            return True

        yield self.register(pinUpdated, 'com.example.pinUpdated')
        self.log.info("procedure pinUpdated() registered")

        def registerNewDevice(deviceID):
            self.log.info("Device {deviceID} registered",deviceID=deviceID)
            r.rpush(registeredDeviceIDs, deviceID)

        yield self.register(registerNewDevice, 'com.example.registerNewDevice')
        self.log.info("procedure registerNewDevice() registered")


        # PUBLISH and CALL every second .. forever
        #
        while True:

            # PUBLISH an event
            #
            if r.llen(registeredDeviceIDs) > 0:
                deviceID = r.rpoplpush(registeredDeviceIDs, notifiedDeviceIDs)
                pin = randrange(0, 99)
                value = randrange(0, 255)

                yield self.publish('com.example.' + str(deviceID), pin, value)
                self.log.info("Published to Device {deviceID}: pin {x} should update to {y}",deviceID=deviceID, x=pin, y=value)
            elif r.exists(notifiedDeviceIDs):
                r.rename(notifiedDeviceIDs, registeredDeviceIDs)
                yield sleep(1)
            else:
                yield sleep(1)

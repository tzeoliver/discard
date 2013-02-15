import gevent.monkey
gevent.monkey.patch_all()

import bottle
import socketio.server
import socketio.namespace
import socketio.mixins

class CardNamespace(socketio.namespace.BaseNamespace, socketio.mixins.BroadcastMixin):
    def on_move(self, position):
        print "Position", position
        self.broadcast_event_not_me("move", position)

@bottle.route("/socket.io/<remaining:path>")
def socketIO(remaining):
    print "Socket.io request"
    socketio.socketio_manage(bottle.request.environ, {'': CardNamespace}, bottle.request)

@bottle.route("/")
@bottle.route("/<file:path>")
def static(file="index.html"):
    print "Serving file", file
    return bottle.static_file(file, root="static")

bottle.debug()
socketio.server.SocketIOServer(("", 8000), bottle.app()).serve_forever()

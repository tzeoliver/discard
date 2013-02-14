import gevent.monkey
gevent.monkey.patch_all()

import bottle

@bottle.route("/")
@bottle.route("/<file:path>")
def static(file="index.html"):
    return bottle.static_file(file, root="static")

bottle.debug()
bottle.run(host="", port=8000, server="gevent")

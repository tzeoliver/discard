import sys
sys.path.insert(0, "lib/bottle")

import bottle
import logging

logging.basicConfig(filename='localDiscard.log',format='%(asctime)s %(message)s',datefmt='%d/%m/%Y %H:%M:%S',level=logging.DEBUG)
logging.info("--- New session started ---")

@bottle.post('/')
def post_log():
    msg = bottle.request.body.read()
    logging.info(msg)
    print msg
    bottle.response.headers['Access-Control-Allow-Origin'] = '*' 
    
bottle.debug()
logging.info("Starting local Discard Bottle server")
bottle.run(host='localhost', port=8989, debug=True)
logging.info("--- Session ended ---")
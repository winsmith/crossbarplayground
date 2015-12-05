import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)
pin_queue = "pin_queue"

def start_worker():
    while True:
        new_set_pin = r.blpop(pin_queue) # this command blocks until the queue is no longer empty
        print "Got new pin from queue:", new_set_pin

if __name__ == "__main__":
    start_worker()
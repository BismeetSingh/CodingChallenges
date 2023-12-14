import asyncio
import tornado
import reprlib
import argparse
import requests
import time
from repeat_timer import RepeatTimer

SERVERS = ['http://localhost:8080/','http://localhost:8081/','http://localhost:8082/']
FAILED_SERVERS = []
currentIndex = -1
healthTimeout = 0
STATUS_OK = 200

class MainHandler(tornado.web.RequestHandler):


    def get(self):

        server = self.return_server()
        if not server:
            self.write("No Server available to serve requests")
        # self.write(f'Request processed by {server}')
        self.write('\n')
        startTime = time.time()
        response = requests.get(server)
        endTime = time.time()
        # self.write(f'took {(endTime - startTime)} milliseconds to process request')
        self.write('\n')
        print(response.text)
        message = f"Request Received from host: {reprlib.repr(self.request.host)}\n"
        message += f"Request uses method: {reprlib.repr(self.request.method)}\n"
        message += f"Request processed by: {server}\n"
        message += f"in {endTime - startTime} seconds"
        self.write(message)
                                        
   

    def return_server(self):
        if not SERVERS:
            return None
        global currentIndex
        server = SERVERS[(currentIndex+1) % len(SERVERS)]
        currentIndex+=1
        return server

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

def health_check():
        global currentIndex
        # print('Called health check function')
        
        for server in FAILED_SERVERS:
            try:
                response = requests.get(server)
                if response.status_code == STATUS_OK:
                    print(f'{server} is back up')
                    SERVERS.append(server)
            except Exception as e:
                print(e)

        for server in SERVERS:
            if server in FAILED_SERVERS:
                FAILED_SERVERS.remove(server)

        for server in SERVERS:
            try:
                response = requests.get(server)
                if response.status_code != STATUS_OK:
                    print(f'{server} is down')
                    FAILED_SERVERS.append(server)
            except Exception as e:
                print(f'{server} is down with {e}')
                FAILED_SERVERS.append(server)

        for server in FAILED_SERVERS:
            if server in SERVERS:
                SERVERS.remove(server)


async def main():
    app = make_app()
    app.listen(8888)
    parser = argparse.ArgumentParser(description='A Basic Load Balancer')
    parser.add_argument("--h", help="Health check at every h seconds",default=5)
    args = parser.parse_args()
    global healthTimeout
    healthTimeout = args.h
    timer = RepeatTimer(healthTimeout,health_check)  
    timer.start() #recalling run  
    print('Threading started')  
    await asyncio.Event().wait()

# if __name__ == "__main__":
asyncio.run(main())

##We are now creating a thread timer and controling it  

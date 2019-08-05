import socket
import sys
import os
import time
import threading
import asyncio
import websockets


class PiSugarServer:

    SERVER_ADDRESS = '/tmp/pisugar.sock'
    WEBSOCKET_PORT = 3001
    CORE = None

    def __init__(self, core):
        self.CORE = core
        self.create_ws_server()
        threading.Thread(name="server_thread_shell", target=self.socket_server, args=(self.SERVER_ADDRESS, True)).start()

    def socket_server(self, server_address, once):
        try:
            os.unlink(server_address)
        except OSError:
            if os.path.exists(server_address):
                raise
        # Create a UDS socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Bind the socket to the port
        print(sys.stderr, 'starting up on %s' % server_address)
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)

        while True:
            # Wait for a connection
            connection, client_address = sock.accept()
            try:
                while True:
                    data = connection.recv(64)
                    if data:
                        # print(sys.stderr, 'sending data back to the client')
                        response = self.socket_handler(data)
                        connection.sendall(response)
                        break
                    else:
                        print(sys.stderr, 'no more data from', client_address)
                        break
                if once:
                    connection.close()
            finally:
                # Clean up the connection
                if once:
                    connection.close()

    def socket_handler(self, data, is_string=False):
        if is_string:
            req_str = data.replace("\n", "")
        else:
            req_str = str(data.decode(encoding="utf-8")).replace("\n", "")
        print(req_str)
        req_arr = req_str.split(" ")
        res_str = ""
        try:
            if req_arr[0] == "get":
                if req_arr[1] == "model":
                    res_str = self.CORE.get_model()
                if req_arr[1] == "battery":
                    res_str = str(self.CORE.BATTERY_LEVEL)
                if req_arr[1] == "battery_v":
                    res_str = str(self.CORE.BATTERY_V)
                if req_arr[1] == "battery_i":
                    res_str = str(self.CORE.BATTERY_I)
                if req_arr[1] == "battery_charging":
                    res_str = str(self.CORE.IS_CHARGING)
                if req_arr[1] == "rtc_time":
                    res_str = time.strftime("%w %b %d %H:%M:%S %Y", self.CORE.RTC_TIME)
                if req_arr[1] == "rtc_time_list":
                    print(self.CORE.RTC_TIME_LIST)
                    res_str = str(self.CORE.RTC_TIME_LIST)
                if req_arr[1] == "rtc_clock_flag":
                    res_str = str(self.CORE.read_clock_flag())

                res_str = req_arr[1] + ": " + res_str

            if req_arr[0] == "rtc_clean_flag":
                self.CORE.clean_clock_flag()
                res_str = req_arr[0] + ": done"
            if req_arr[0] == "rtc_pi2rtc":
                self.CORE.sync_time_pi2rtc()
                res_str = req_arr[0] + ": done"
            if req_arr[0] == "rtc_clock_set":
                argv1 = req_arr[1]
                argv2 = req_arr[2]
                try:
                    time_arr = list(map(int, argv1.split(",")))
                    week_repeat = int(argv2, 2)
                    self.CORE.clock_time_set([time_arr[0], time_arr[1], time_arr[2], time_arr[3], time_arr[4], time_arr[5], time_arr[6]], week_repeat)
                    self.CORE.clean_clock_flag()
                    res_str = req_arr[0] + ": done"
                except Exception as e:
                    print(e)
                    return bytes('Invalid arguments.' + "\n", encoding='utf-8')
            if req_arr[0] == "rtc_test_wake":
                self.CORE.set_test_wake()
                res_str = req_arr[0] + ": wakeup after 1 min 30 sec"
        except Exception as e:
            print(e)
            return bytes('Invalid arguments.' + "\n", encoding='utf-8')
        return bytes(res_str + "\n", encoding='utf-8')

    def create_ws_server(self):
        print("Start websocket server on port %d..." % self.WEBSOCKET_PORT)
        start_server = websockets.serve(self.ws_handler, "0.0.0.0", self.WEBSOCKET_PORT)
        asyncio.get_event_loop().run_until_complete(start_server)
        threading.Thread(name="server_thread_ws", target=asyncio.get_event_loop().run_forever).start()

    async def ws_handler(self, websocket, path):
        while True:
            data = await websocket.recv()
            response = self.socket_handler(data, is_string=True)
            await websocket.send(response)

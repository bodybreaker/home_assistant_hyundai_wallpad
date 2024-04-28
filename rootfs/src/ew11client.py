import socket
import threading
import json
import time
from logger import logger

class EW11Client:
    START_FLAG = "f7"
    MAX_TRY_RCV_CNT = 7

    def __init__(self,server,port):
        self.isRun = False
        
        self.server = server
        self.port = port
    
    def start(self,message_event_handler):
        self.message_event_handler = message_event_handler
        self.isWaiting_rcv = False
        logger.info(f"Socket 연결 시도")
        self.isRun=True
        self.soc = socket.socket()
        self.soc.settimeout(None)
        try:
            self.soc.connect((self.server, int(self.port)))
        except Exception as e:
            logger.info(f"Socket 연결 실패 >> {self.server}:{self.port}")
            return False

        logger.info(f"Socket 연결 완료 >> {self.server}:{self.port}")
        self.loop_thread = threading.Thread(target=self._loop,args=())
        self.loop_thread.start()

    def on_message(self,message):
        if self.isWaiting_rcv == True:
            if self.waiting_rcv_msg in message.lower():
                self.isWaiting_rcv = False
        self.message_event_handler(message.lower())

    def send_message(self,send_cmd,rcv_cmd):
        self.waiting_rcv_msg = rcv_cmd.lower()
        self.isWaiting_rcv = True
        # 커맨드 정상 체크
        for i in range(EW11Client.MAX_TRY_RCV_CNT):
            # broken pipe 방지
            try:
                self.soc.send(bytearray.fromhex((send_cmd)))
            except Exception as e:
                logger.info(f"Socket send 실패 >> {e}")
                self.soc = socket.socket()
                self.soc.settimeout(None)
                self.soc.connect((self.server, int(self.port)))           
            if self.isWaiting_rcv == False:
                logger.info(f"{send_cmd} 명령 성공")
                return True
            time.sleep(0.5)
        logger.info(f"{send_cmd} 명령 실패 (rcv 패킷 수신 실패)")
        return False

    def _loop(self):
        buf = []
        start_flag = False
        read_index = 1 # 두번째 패킷이 패킷의 길이 변수
        packet_len = 0
        while self.isRun:
            try:
                data = self.soc.recv(1)
                if len(data) == 0:
                    pass
                raw_hex = data.hex()
                if raw_hex == EW11Client.START_FLAG:
                    start_flag = True
                #  시작 flag True 이후 데이터 읽어야 함
                if start_flag == True:
                    buf.append(raw_hex)
                    # 패킷 길이 변수
                    if read_index==2:
                        packet_len = int(raw_hex, 16)
                        # logger.info(packet_len)
                    if (read_index == packet_len) and packet_len>1:
                        # logger.info(buf)
                        result = ' '.join(buf)
                        self.on_message(result)
                        buf = []
                        read_index=0
                        packet_len=0
                        start_flag=False
                    read_index+=1
            except Exception as e:
                logger.info(f"Error receiving data: {e}")

    def stop(self):
        self.isRun = False
        self.soc.close()

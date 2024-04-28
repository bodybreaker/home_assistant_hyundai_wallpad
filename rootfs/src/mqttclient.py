import paho.mqtt.client as mqtt
import threading
import json
from logger import logger

class MQTTClient:
    def __init__(self,server,port,user_name,user_pass):
        self.isRun = False
        self.server = server
        self.port = port
        self.user_name = user_name
        self.user_pass = user_pass

    # message_event_handler(topic,payload)
    def start(self,message_event_handler):
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.mqtt_client.on_message = self._on_message
        self.message_event_handler = message_event_handler
        self.mqtt_client.username_pw_set(username=self.user_name, password=self.user_pass)
        self.mqtt_client.connect(self.server, port=self.port, keepalive=60)
        self.isRun = True
        self.loop_thread = threading.Thread(target=self._loop,args=())
        self.loop_thread.start()

    def _on_message(self,client,obj,msg):
        _topic = msg.topic
        _payload = msg.payload.decode()
        logger.info(_topic)
        self.message_event_handler(_topic,_payload)
        
    def _loop(self):
        try:
            while self.isRun:
                self.mqtt_client.loop()
        except KeyboardInterrupt:
            self.isRun = False
            self.mqtt_client.disconnect()

    def subscribe(self,topic):
        self.mqtt_client.subscribe(topic)

    def publish(self,topic,payload):
        if type(payload)==dict:
            payload_str = json.dumps(payload)
        else:
            payload_str = payload
        self.mqtt_client.publish(topic=topic,payload=payload_str)

    def stop(self):
        self.isRun = False
        self.loop_thread.join()
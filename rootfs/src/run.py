import yaml
from mqttclient import MQTTClient
from ew11client import EW11Client
from logger import logger

logger.info("Start Program")

# 디바이스 패킷 정보 경로
DEVICE_PATH = "src/devices.yaml"

# MQTT 설정
MQTT_USER_NAME = 'homeassistant'
MQTT_USER_PASS = 'siek9owijaiH6Jei9sosh1La8uataiNahtohX8Xoiboonairei9upahy8haezaay'#'mqtt'
MQTT_SERRVER_URL = '192.168.0.60'
MQTT_SERVER_PORT = 1883

# EW11 설정
EW11_SERVER_URL = '192.168.0.12'
EW11_SERVER_PORT = 8899

# MQTT 
TOPIC_HA_PREFIX = "homeassistant"

with open(DEVICE_PATH,'r') as f:
    device_list_info = yaml.safe_load(f)


# HA mqtt 로 부터 기기 제어/상태확인 요청
# set 요청 등이 오면 ew11을 통해 기기 제어 후 state topic 으로 기기 상태 변경해야 반영됨
def mqtt_on_message(topic:str,payload:str):
    # homeassistant/light/bedroom_light1/set
    logger.info(f"[mqtt_on_message] :: {topic} :: {payload}")
    
    parsed_topic = topic.split('/')
    device_type = parsed_topic[1]
    component_name = parsed_topic[2]

    # 조명류
    if device_type =="light":
        topic_state = f"{TOPIC_HA_PREFIX}/{device_type}/{component_name}/state"
        #ew11 제어 요청
        component_info = device_list_info[device_type][component_name]

        control_success = False
        if payload.lower() =="on":
            control_success = ew11Client.send_message(component_info['turn_on'][0],component_info['turn_on'][1])
        elif payload.lower() =="off":
            control_success = ew11Client.send_message(component_info['turn_off'][0],component_info['turn_off'][1])
        if control_success: mqttClient.publish(topic_state,payload)   
    
    # 엘리베이터 
    if device_type =="elevator":
        topic_state = f"{TOPIC_HA_PREFIX}/{device_type}/{component_name}/state"
        #ew11 제어 요청
        component_info = device_list_info[device_type][component_name]

        control_success = False
        if payload.lower() =="press":
            control_success = ew11Client.send_message(component_info['press'][0],component_info['press'][1])
        if control_success: mqttClient.publish(topic_state,payload) 

# 월패드 ew11로 부터 수신하는 메시지
# 엘리베이터 층수 정보
ELEV_IDLE = "f7 0d 01 34 01 41 10 00 00 00 00 9f ee"
ELEV_ARRIVED = "f7 0d 01 34 01 41 10 00 01 04 09 93 ee"
ELEV_UP = "f7 0d 01 34 01 41 10 00 a6"
ELEV_DOWN = "f7 0d 01 34 01 41 10 00 b6"
state_topic_updown = "homeassistant/elevator/updown_sensor/state"
state_topic_floor = "homeassistant/elevator/floor_sensor/state"
state_topic_status = "homeassistant/elevator/status_sensor/state"
def ew11_on_message(message):
    
    if message ==ELEV_IDLE:
        mqttClient.publish(state_topic_status,"대기")
    if message ==ELEV_ARRIVED :
        mqttClient.publish(state_topic_status,"도착")
    if ELEV_UP in message:
        mqttClient.publish(state_topic_updown,"상행")
        mqttClient.publish(state_topic_floor,message.split(' ')[9].lstrip('0'))
    if ELEV_DOWN in message:
        mqttClient.publish(state_topic_updown,"하행")
        mqttClient.publish(state_topic_floor,message.split(' ')[9].lstrip('0'))
        



    # 엘리베이터 관련
    # if "F7 0B 01 34 04 41".lower() in message:
    #     print(message)
    # if message == ELEV_IDLE:
    #     pass
    #logger.info("IDLE")
    #logger.info(f"\t[ew11_on_message] >>> {message} ")

# MQTT 클라이언트 시작
mqttClient = MQTTClient(server=MQTT_SERRVER_URL,port=MQTT_SERVER_PORT,user_name=MQTT_USER_NAME,user_pass=MQTT_USER_PASS)
mqttClient.start(mqtt_on_message)

# EW11 클라이언트 시작
ew11Client = EW11Client(EW11_SERVER_URL,EW11_SERVER_PORT)
ew11Client.start(ew11_on_message)


# MQTT 장치 퍼블리싱 시작
dev_type_list = list(device_list_info.keys())

for d_type in dev_type_list:
    logger.info(f'■■■■ 기기 종류 >> {d_type}')
    dev_arr = device_list_info[d_type] 
    
    if d_type=="light":
        for component_name in dev_arr:
            #logger.info(f"{component_name} - {device_list_info[d_type][component_name]}")
            device_name = device_list_info[d_type][component_name]['dev_name']
            component_type = device_list_info[d_type][component_name]['component_type']
            # topic_command 는 subscribe
            topic_command = f"{TOPIC_HA_PREFIX}/{d_type.lower()}/{component_name}/set"
            # topic_config 와 payload 는 mqtt 로 publish
            topic_config = f"{TOPIC_HA_PREFIX}/{component_type}/{component_name}/config"
            topic_state = f"{TOPIC_HA_PREFIX}/{d_type.lower()}/{component_name}/state"
            discovery_palylaod =  {
                "name": f"{component_name}",
                "object_id":f"{device_name}_{component_name}",
                "unique_id": f"{device_name}_{component_name}",
                "device":{
                    "identifiers":device_name,
                    'name':device_name,
                    'manufacturer':"Minwoo Park"
                },
                "retain":True
            }
            discovery_palylaod['state_topic'] = topic_state
            discovery_palylaod['command_topic'] = topic_command

            mqttClient.publish(topic_config,discovery_palylaod)
            mqttClient.subscribe(topic_command)

            logger.info(f"\t topic_command [subscribe from mqtt] >> {topic_command}")
            logger.info(f"\t topic_config  [publish to mqtt]>> {topic_config}")
            logger.info(f"\t\t discovery_palylaod>> {discovery_palylaod}")
            logger.info(f"{'-'*50}\n")
            #
    if d_type=="elevator":
        for component_name in dev_arr:
            device_name = device_list_info[d_type][component_name]['dev_name']
            component_type = device_list_info[d_type][component_name]['component_type']
            topic_config = f"{TOPIC_HA_PREFIX}/{component_type}/{component_name}/config"
            topic_state = f"{TOPIC_HA_PREFIX}/{d_type.lower()}/{component_name}/state"
            discovery_palylaod =  {
                "name": f"{component_name}",
                "object_id":f"{device_name}_{component_name}",
                "unique_id": f"{device_name}_{component_name}",
                "device":{
                    "identifiers":device_name,
                    'name':device_name,
                    'manufacturer':"Minwoo Park"
                },
                "retain":False
            }
            discovery_palylaod['state_topic'] = topic_state

            topic_command = f"{TOPIC_HA_PREFIX}/{d_type.lower()}/{component_name}/set"
            if component_type in ['button']:
                mqttClient.subscribe(topic_command)
                discovery_palylaod['command_topic'] = topic_command
                logger.info(f"\t topic_command [subscribe from mqtt] >> {topic_command}")
            mqttClient.publish(topic_config,discovery_palylaod)
                           
            logger.info(f"\t topic_config  [publish to mqtt]>> {topic_config}")
            logger.info(f"\t\t discovery_palylaod>> {discovery_palylaod}")
            logger.info(f"{'-'*50}\n")
#     for dev in dev_arr:
#         print(type(dev))

# print(device_list_info)
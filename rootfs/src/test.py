from ew11client import EW11Client
from logger import logger

# https://yogyui.tistory.com/entry/%ED%98%84%EB%8C%80%ED%86%B5%EC%8B%A0-%EC%9B%94%ED%8C%A8%EB%93%9C-RS-485-%ED%86%B5%EC%8B%A0-%ED%94%84%EB%A1%9C%ED%86%A0%EC%BD%9C-%EB%AA%85%EC%84%B8-%EA%B3%B5%ED%86%B5-%EC%82%AC%EC%96%91

#
DEVICE_MAP = {
    "15": "감성 조명",
    "18": "난방",
    "19": "일반 조명",
    "1A": "디밍(dimming) 조명",
    "1B": "주방 도시가스 밸브",
    "1C": "시스템 에어컨",
    "1E": "현관 도어락",
    "1F": "아울렛 (대기전력 차단 콘센트)",
    "2A": "일괄소등 스위치",
    "2B": "전열교환기 (환기)",
    "34": "엘리베이터",
    "43": "HEMS",
    "44": "현재 시간"
}

def ew11_on_message(message):
    parts = message.strip().split()
    #logger.info(parts[3].upper())
    isKnown =False
    for code, description in DEVICE_MAP.items():
        if parts[3].upper()==code:
            isKnown = True
            logger.info(description+" : "+message)
    if not isKnown:
        logger.error("🌍🌍 미분류 : " +message)
    

EW11_SERVER_URL = 'mwds.shop'
EW11_SERVER_PORT = 8899

logger.info("테스트 시작")

ew11Client = EW11Client(EW11_SERVER_URL,EW11_SERVER_PORT)
ew11Client.start(ew11_on_message)

# https://yogyui.tistory.com/entry/%ED%98%84%EB%8C%80%ED%86%B5%EC%8B%A0-%EC%9B%94%ED%8C%A8%EB%93%9C-RS-485-%ED%86%B5%EC%8B%A0-%ED%94%84%EB%A1%9C%ED%86%A0%EC%BD%9C-%EB%AA%85%EC%84%B8-%EA%B3%B5%ED%86%B5-%EC%82%AC%EC%96%91

# f7391f0100d020
logger.info("f7 39 1f 01 00 d0 20".upper())
ew11Client.send_message("f7 39 1f 01 00 d0 20".upper(),"")
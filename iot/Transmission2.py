#
# import paho.mqtt.client as mqtt
# import json
# import time
# import logging
# from enum import Enum
# from typing import Optional
#
#
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s-%(levelname)s-%(message)s'
# )
# logger = logging.getLogger(__name__)
#
#
#
# class StateBarrier(Enum):
#     STOP = 0
#     MOVE = 1
#
#
# class DirectionBarrier(Enum):
#     LEFT = 0
#     RIGHT = 1
#
#
# class MQTTConfig:
#     BROKER = "broker.hivemq.com"
#     PORT = 1883
#     TOPIC = "barrier_condition"
#     KEEPALIVE = 60
#     QOS = 1
#     RECONNECT_DELAY = 5
#
#
# class MQTTClient:
#
#     def __init__(self, broker: str, port: int, topic: str):
#         self.broker = broker
#         self.port = port
#         self.topic = topic
#         self.client: Optional[mqtt.Client] = None
#         self.connected = False
#
#     def on_connect(self, client, userdata, flags, rc,properties= None):
#
#         warning_numbers = {
#             0: "Successfull",
#             1: "Warning To Protocol Version",
#             2: "Invalid Client ID",
#             3: "Server Unvaliable",
#             4: "Invalid Username/Password",
#             5: "Unauthoried Access"
#         }
#
#         if (rc == 0):
#             self.connected = True
#             client.subscribe(self.topic, qos=MQTTConfig.QOS)
#             logger.info(f"Subscribed to topic: {self.topic}")
#             logger.info(f"Connected To MQTT Broker : {self.broker} , {self.port}")
#         else:
#             self.connected = False
#
#             logger.error(f"Connection Warning : {warning_numbers.get(rc, 'Unknown Warning')} , (code : {rc})")
#
#     def on_message(self, client, userdata, message):
#
#         try:
#             msg_payload = message.payload.decode('utf-8')
#             logger.info(f"Message Received [{message.topic}]: {msg_payload}")
#
#
#             data = json.loads(msg_payload)
#             print(data["status"])
#
#         except Exception as e:
#             logger.error(f"Message Processing Error: {e}")
#
#     def on_disconnect(self, client, userdata,flags, rc,properties = None):
#         self.connected = False
#         if (rc != 0):
#             logger.warning(f"Unexpected Warning (Code : {rc})")
#
#     def on_publish(self, client, userdata,flags, mid,properties = None):
#         logger.debug(f"Recieved Message : (ID : {mid})")
#
#     def connect(self) -> bool:
#         try:
#             client_id = f"Barrier_control_{int(time.time())}"
#             self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id=client_id)
#
#             self.client.on_connect = self.on_connect
#             self.client.on_disconnect = self.on_disconnect
#             self.client.on_publish = self.on_publish
#             self.client.on_message = self.on_message
#
#             self.client.connect(self.broker, self.port, MQTTConfig.KEEPALIVE)
#             self.client.loop_start()
#
#
#
#             time.sleep(1)
#             return True
#
#         except Exception as e:
#             logger.error(f"Connection Warning : {e}")
#             return False
#
#     def SendOrder(self, status: StateBarrier, direction: DirectionBarrier) -> bool:
#         if not self.connected:
#             logger.error(f"MQTT Connection Could Not Be Established.")
#             return False
#
#         try:
#             data_package = {
#                 "status": status.value,
#                 "direction": direction.value,
#                 "timestamp": int(time.time())
#             }
#
#             json_message = json.dumps(data_package)
#
#             product = self.client.publish(
#                 self.topic,
#                 json_message,
#                 qos=MQTTConfig.QOS,
#                 retain=False
#             )
#
#
#             product.wait_for_publish()
#
#             if product.rc == mqtt.MQTT_ERR_SUCCESS:
#                 logger.info(f"Transmitted... {json_message} : {status.name} : {direction.name}")
#                 return True
#             else:
#                 logger.error(f"Message could not be sent. error code : {product.rc}")
#
#         except Exception as e:
#             logger.error(f"Shipping error: {e}")
#             return False
#
#     def disconnect(self):
#         if self.client:
#             self.client.loop_stop()
#             self.client.disconnect()
#             logger.info("Disconnected MQTT Broker")
#
#
#
# def main():
#     mqtt_client = MQTTClient(
#         broker=MQTTConfig.BROKER,
#         port=MQTTConfig.PORT,
#         topic=MQTTConfig.TOPIC
#     )
#
#     if not mqtt_client.connect():
#         logger.error(f"Unable To Connect To MQTT Broker.")
#         return
#
#
#     try:
#         while True:
#
#             time.sleep(1)
#
#
#
#     except Exception as e:
#         logger.error(f"Unexpexted Error : {e}")
#
#
# if __name__ == "__main__":
#     main()
import paho.mqtt.client as mqtt
import json
import time
import logging
from enum import Enum
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StateBarrier(Enum):
    """Bariyer durumu"""
    STOP = 0  # Bariyer kapalı (trafik akışını durdur)
    MOVE = 1  # Bariyer açık (trafik akışına izin ver)


class DirectionBarrier(Enum):
    """Bariyer yönü"""
    LEFT = 0  # Sol taraf bariyeri
    RIGHT = 1  # Sağ taraf bariyeri


class MQTTConfig:
    """MQTT yapılandırma sabitleri"""
    BROKER = "broker.hivemq.com"
    PORT = 1883
    TOPIC = "barrier_condition"
    KEEPALIVE = 60
    QOS = 1
    RECONNECT_DELAY = 5


class MQTTClient:
    """MQTT istemci sınıfı - Bariyer kontrol mesajlarını gönderir"""

    def __init__(self, broker: str, port: int, topic: str):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client: Optional[mqtt.Client] = None
        self.connected = False

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Bağlantı kurulduğunda çağrılır"""
        warning_numbers = {
            0: "Successful",
            1: "Warning To Protocol Version",
            2: "Invalid Client ID",
            3: "Server Unavailable",
            4: "Invalid Username/Password",
            5: "Unauthorized Access"
        }

        if rc == 0:
            self.connected = True
            client.subscribe(self.topic, qos=MQTTConfig.QOS)
            logger.info(f"Subscribed to topic: {self.topic}")
            logger.info(f"Connected to MQTT Broker: {self.broker}:{self.port}")
        else:
            self.connected = False
            logger.error(f"Connection Warning: {warning_numbers.get(rc, 'Unknown Warning')} (code: {rc})")

    def on_message(self, client, userdata, message):
        """Mesaj alındığında çağrılır"""
        try:
            msg_payload = message.payload.decode('utf-8')
            logger.info(f"Message Received [{message.topic}]: {msg_payload}")

            data = json.loads(msg_payload)
            logger.info(f"Parsed data - Status: {data.get('status')}, Direction: {data.get('direction')}")

        except Exception as e:
            logger.error(f"Message Processing Error: {e}")

    def on_disconnect(self, client, userdata, flags, rc, properties=None):
        """Bağlantı kesildiğinde çağrılır"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected Disconnection (Code: {rc})")

    def on_publish(self, client, userdata, mid, reason_code=None, properties=None):
        """Mesaj yayınlandığında çağrılır"""
        logger.debug(f"Message Published (ID: {mid})")

    def connect(self) -> bool:
        """MQTT broker'a bağlan"""
        try:
            client_id = f"Barrier_control_{int(time.time())}"
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)

            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            self.client.on_message = self.on_message

            self.client.connect(self.broker, self.port, MQTTConfig.KEEPALIVE)
            self.client.loop_start()

            # Bağlantının kurulması için kısa bir bekleme
            time.sleep(1)
            return True

        except Exception as e:
            logger.error(f"Connection Error: {e}")
            return False

    def SendOrder(self, status: StateBarrier, direction: DirectionBarrier) -> bool:
        """Bariyer kontrol mesajı gönder"""
        if not self.connected:
            logger.error("MQTT connection is not established.")
            return False

        try:
            data_package = {
                "status": status.value,
                "direction": direction.value,
                "status_name": status.name,
                "direction_name": direction.name,
                "timestamp": int(time.time())
            }

            json_message = json.dumps(data_package)

            result = self.client.publish(
                self.topic,
                json_message,
                qos=MQTTConfig.QOS,
                retain=False
            )

            result.wait_for_publish()

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"✓ Transmitted: {status.name} | {direction.name} | {json_message}")
                return True
            else:
                logger.error(f"Message could not be sent. Error code: {result.rc}")
                return False

        except Exception as e:
            logger.error(f"Sending error: {e}")
            return False

    def disconnect(self):
        """MQTT bağlantısını kapat"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT Broker")


def main():
    """Test amaçlı ana fonksiyon"""
    mqtt_client = MQTTClient(
        broker=MQTTConfig.BROKER,
        port=MQTTConfig.PORT,
        topic=MQTTConfig.TOPIC
    )

    if not mqtt_client.connect():
        logger.error("Unable to connect to MQTT Broker.")
        return

    try:
        # Test mesajları gönder
        logger.info("Sending test messages...")

        time.sleep(2)
        mqtt_client.SendOrder(StateBarrier.MOVE, DirectionBarrier.LEFT)

        time.sleep(2)
        mqtt_client.SendOrder(StateBarrier.STOP, DirectionBarrier.LEFT)

        time.sleep(2)
        mqtt_client.SendOrder(StateBarrier.MOVE, DirectionBarrier.RIGHT)

        time.sleep(2)
        mqtt_client.SendOrder(StateBarrier.STOP, DirectionBarrier.RIGHT)

        # Mesajları dinlemeye devam et
        logger.info("Listening for messages... (Press Ctrl+C to exit)")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        mqtt_client.disconnect()


if __name__ == "__main__":
    main()
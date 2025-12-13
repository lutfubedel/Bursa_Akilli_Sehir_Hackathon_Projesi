
import paho.mqtt.client as mqtt
import json
import time
import logging
from enum import Enum
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s-%(levelname)s-%(message)s'
)
logger = logging.getLogger(__name__)



class StateBarrier(Enum):
    STOP = 0
    MOVE = 1


class DirectionBarrier(Enum):
    LEFT = 0
    RIGHT = 1


class MQTTConfig:
    BROKER = "broker.hivemq.com"
    PORT = 1883
    TOPIC = "barrier_condition"
    KEEPALIVE = 60
    QOS = 1
    RECONNECT_DELAY = 5


class MQTTClient:

    def __init__(self, broker: str, port: int, topic: str):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client: Optional[mqtt.Client] = None
        self.connected = False

    def on_connect(self, client, userdata, flags, rc,properties= None):

        warning_numbers = {
            0: "Successfull",
            1: "Warning To Protocol Version",
            2: "Invalid Client ID",
            3: "Server Unvaliable",
            4: "Invalid Username/Password",
            5: "Unauthoried Access"
        }

        if (rc == 0):
            self.connected = True
            client.subscribe(self.topic, qos=MQTTConfig.QOS)
            logger.info(f"Subscribed to topic: {self.topic}")
            logger.info(f"Connected To MQTT Broker : {self.broker} , {self.port}")
        else:
            self.connected = False

            logger.error(f"Connection Warning : {warning_numbers.get(rc, 'Unknown Warning')} , (code : {rc})")

    def on_message(self, client, userdata, message):

        try:
            msg_payload = message.payload.decode('utf-8')
            logger.info(f"Message Received [{message.topic}]: {msg_payload}")


            data = json.loads(msg_payload)
            print(data["status"])

        except Exception as e:
            logger.error(f"Message Processing Error: {e}")

    def on_disconnect(self, client, userdata,flags, rc,properties = None):
        self.connected = False
        if (rc != 0):
            logger.warning(f"Unexpected Warning (Code : {rc})")

    def on_publish(self, client, userdata,flags, mid,properties = None):
        logger.debug(f"Recieved Message : (ID : {mid})")

    def connect(self) -> bool:
        try:
            client_id = f"Barrier_control_{int(time.time())}"
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id=client_id)

            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            self.client.on_message = self.on_message

            self.client.connect(self.broker, self.port, MQTTConfig.KEEPALIVE)
            self.client.loop_start()



            time.sleep(1)
            return True

        except Exception as e:
            logger.error(f"Connection Warning : {e}")
            return False

    def SendOrder(self, status: StateBarrier, direction: DirectionBarrier) -> bool:
        if not self.connected:
            logger.error(f"MQTT Connection Could Not Be Established.")
            return False

        try:
            data_package = {
                "status": status.value,
                "direction": direction.value,
                "timestamp": int(time.time())
            }

            json_message = json.dumps(data_package)

            product = self.client.publish(
                self.topic,
                json_message,
                qos=MQTTConfig.QOS,
                retain=False
            )


            product.wait_for_publish()

            if product.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Transmitted... {json_message} : {status.name} : {direction.name}")
                return True
            else:
                logger.error(f"Message could not be sent. error code : {product.rc}")

        except Exception as e:
            logger.error(f"Shipping error: {e}")
            return False

    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected MQTT Broker")



def main():
    mqtt_client = MQTTClient(
        broker=MQTTConfig.BROKER,
        port=MQTTConfig.PORT,
        topic=MQTTConfig.TOPIC
    )

    if not mqtt_client.connect():
        logger.error(f"Unable To Connect To MQTT Broker.")
        return


    try:
        while True:

            time.sleep(1)



    except Exception as e:
        logger.error(f"Unexpexted Error : {e}")


if __name__ == "__main__":
    main()

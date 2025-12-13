
import paho.mqtt.client as mqtt
import json
import time
import logging
import random
from enum import Enum
from threading import Thread, Event
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StateBarrier(Enum):
    STOP = 0
    MOVE = 1

class DirectionBarrier(Enum):
    LEFT = 0
    RIGHT = 1

class SimulatorConfig:

    BROKER = "broker.hivemq.com"
    PORT = 1883
    TOPIC = "barrier_condition"  # Ana kodunuzdaki topic ile aynı olmalı
    QOS = 1
    KEEPALIVE = 60


class MQTTSimulator:

    
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        self.stop_event = Event()
        
    def on_connect(self, client, userdata, flags, rc):

        if rc == 0:
            self.connected = True
            logger.info(f"Simulator Connected To Broker: {SimulatorConfig.BROKER}")
        else:
            self.connected = False
            logger.error(f"Connection Failed With Code: {rc}")
    
    def on_disconnect(self, client, userdata, rc):

        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected Disconnection (Code: {rc})")
    
    def on_publish(self, client, userdata, mid):

        logger.debug(f"Message Published (ID: {mid})")
    
    def connect(self) -> bool:

        try:
            client_id = f"simulator_{int(time.time())}"
            self.client = mqtt.Client(client_id=client_id)
            
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            
            logger.info(f"Connecting To {SimulatorConfig.BROKER}:{SimulatorConfig.PORT}...")
            self.client.connect(SimulatorConfig.BROKER, SimulatorConfig.PORT, SimulatorConfig.KEEPALIVE)
            self.client.loop_start()
            
            time.sleep(2)
            return self.connected
            
        except Exception as e:
            logger.error(f"Connection Error: {e}")
            return False
    
    def send_command(self, status: StateBarrier, direction: DirectionBarrier) -> bool:
        """Komut gönder"""
        if not self.connected:
            logger.error("Not Connected To Broker")
            return False
        
        try:
            data = {
                "status": status.value,
                "direction": direction.value,
                "timestamp": int(time.time())
            }
            
            json_message = json.dumps(data)
            result = self.client.publish(
                SimulatorConfig.TOPIC,
                json_message,
                qos=SimulatorConfig.QOS,
                retain=False
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                status_icon = "🛑" if status == StateBarrier.STOP else "▶️"
                dir_icon = "⬅️" if direction == DirectionBarrier.LEFT else "➡️"
                logger.info(f"SENT: {json_message}")
                logger.info(f"   {status_icon} {status.name} | {dir_icon} {direction.name}")
                return True
            else:
                logger.error(f"Publish failed (Code: {result.rc})")
                return False
                
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    def disconnect(self):

        self.stop_event.set()
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("🔌 Disconnected From Broker")


class ThreadedSimulation:

    def __init__(self, simulator: MQTTSimulator):
        self.simulator = simulator
        self.thread: Optional[Thread] = None
        self.running = False
    
    def start(self, simulation_func, *args, **kwargs):

        if self.running:
            logger.warning("Simulation Already Running!")
            return
        
        self.running = True
        self.thread = Thread(
            target=self._run_simulation,
            args=(simulation_func,) + args,
            kwargs=kwargs,
            daemon=True
        )
        self.thread.start()
        logger.info("Simulation Thread Started")



    
    def _run_simulation(self, simulation_func, *args, **kwargs):

        try:
            simulation_func(self.simulator, *args, **kwargs)
        except Exception as e:
            logger.error(f"Simulation Error: {e}")
        finally:
            self.running = False
            logger.info("Simulation Thread Finished")



    
    def stop(self):

        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)





def automatic_simulation(simulator: MQTTSimulator):

    logger.info("\n" + "="*70)
    logger.info("AUTOMATIC SIMULATION - Working On Thread")
    logger.info("="*70 + "\n")
    
    scenarios = [
        (StateBarrier.MOVE, DirectionBarrier.RIGHT, "Start Moving Right", 3),
        (StateBarrier.MOVE, DirectionBarrier.LEFT, "Start Moving Left", 3),
        (StateBarrier.STOP, DirectionBarrier.RIGHT, "Emergency Stop", 2),
        (StateBarrier.MOVE, DirectionBarrier.RIGHT, "Resume Right", 3),
        (StateBarrier.STOP, DirectionBarrier.LEFT, "Final Stop", 1),
    ]
    
    for i, (status, direction, desc, delay) in enumerate(scenarios, 1):
        logger.info(f"\n{'─'*70}")
        logger.info(f"Test {i}/5: {desc}")
        logger.info(f"{'─'*70}")
        
        simulator.send_command(status, direction)
        
        if i < len(scenarios):
            logger.info(f"Waiting {delay} seconds...")
            time.sleep(delay)
    
    logger.info("\n" + "="*70)
    logger.info("AUTOMATIC SIMULATION COMPLETED")
    logger.info("="*70 + "\n")



def random_simulation(simulator: MQTTSimulator, count: int = 15, interval: float = 2.0):

    logger.info("\n" + "="*70)
    logger.info(f"RANDOM SIMULATION - {count} commands, {interval}s interval")
    logger.info("="*70 + "\n")
    
    for i in range(count):
        status = random.choice(list(StateBarrier))
        direction = random.choice(list(DirectionBarrier))
        
        logger.info(f"\nRandom Command {i+1}/{count}")
        simulator.send_command(status, direction)
        
        if i < count - 1:
            time.sleep(interval)
    
    logger.info("\n" + "="*70)
    logger.info("RANDOM SIMULATION COMPLETED")
    logger.info("="*70 + "\n")

def continuous_simulation(simulator: MQTTSimulator, duration: int = 60):

    logger.info("\n" + "="*70)
    logger.info(f"CONTINUOUS SIMULATION - Running for {duration} seconds")
    logger.info("="*70 + "\n")
    
    start_time = time.time()
    count = 0
    
    while (time.time() - start_time) < duration:
        status = random.choice(list(StateBarrier))
        direction = random.choice(list(DirectionBarrier))
        
        simulator.send_command(status, direction)
        count += 1
        
        time.sleep(random.uniform(1.5, 3.5))
    
    logger.info("\n" + "="*70)
    logger.info(f"CONTINUOUS SIMULATION COMPLETED - {count} commands sent")
    logger.info("="*70 + "\n")

def vision_simulation(simulator: MQTTSimulator):

    logger.info("\n" + "="*70)
    logger.info("VISION DETECTION SIMULATION")
    logger.info("="*70 + "\n")
    
    scenarios = [
        ("No object detected", StateBarrier.STOP, DirectionBarrier.RIGHT, 2),
        ("Object detected on RIGHT", StateBarrier.MOVE, DirectionBarrier.RIGHT, 3),
        ("Object moving LEFT", StateBarrier.MOVE, DirectionBarrier.LEFT, 3),
        ("Multiple objects - RIGHT priority", StateBarrier.MOVE, DirectionBarrier.RIGHT, 2),
        ("Lost tracking", StateBarrier.STOP, DirectionBarrier.RIGHT, 2),
        ("Reacquired on LEFT", StateBarrier.MOVE, DirectionBarrier.LEFT, 3),
        ("Object too close - STOP", StateBarrier.STOP, DirectionBarrier.RIGHT, 2),
    ]
    
    for i, (detection, status, direction, delay) in enumerate(scenarios, 1):
        logger.info(f"\nFrame {i}: {detection}")
        simulator.send_command(status, direction)
        time.sleep(delay)
    
    logger.info("\n" + "="*70)
    logger.info("VISION SIMULATION COMPLETED")
    logger.info("="*70 + "\n")




def stress_test(simulator: MQTTSimulator, duration: int = 30, interval: float = 0.5):

    logger.info("\n" + "="*70)
    logger.info(f"STRESS TEST - {duration}s duration, {interval}s interval")
    logger.info("="*70 + "\n")
    
    start_time = time.time()
    total = 0
    success = 0
    
    while (time.time() - start_time) < duration:
        status = random.choice(list(StateBarrier))
        direction = random.choice(list(DirectionBarrier))
        
        if simulator.send_command(status, direction):
            success += 1
        total += 1
        
        time.sleep(interval)
    
    logger.info("\n" + "="*70)
    logger.info("STRESS TEST RESULTS")
    logger.info("="*70)
    logger.info(f"Total: {total} | Success: {success} | Failed: {total-success}")
    logger.info(f"Success Rate: {(success/total*100):.2f}%")
    logger.info("="*70 + "\n")




def pattern_simulation(simulator: MQTTSimulator, cycles: int = 5):

    logger.info("\n" + "="*70)
    logger.info(f"PATTERN SIMULATION - {cycles} cycles")
    logger.info("="*70 + "\n")
    
    pattern = [
        (StateBarrier.MOVE, DirectionBarrier.RIGHT),
        (StateBarrier.MOVE, DirectionBarrier.RIGHT),
        (StateBarrier.STOP, DirectionBarrier.RIGHT),
        (StateBarrier.MOVE, DirectionBarrier.LEFT),
        (StateBarrier.MOVE, DirectionBarrier.LEFT),
        (StateBarrier.STOP, DirectionBarrier.LEFT),
    ]
    
    for cycle in range(cycles):
        logger.info(f"\nCycle {cycle+1}/{cycles}")
        for i, (status, direction) in enumerate(pattern, 1):
            logger.info(f"Step {i}/{len(pattern)}")
            simulator.send_command(status, direction)
            time.sleep(1.5)
    
    logger.info("\n" + "="*70)
    logger.info("PATTERN SIMULATION COMPLETED")
    logger.info("="*70 + "\n")



def show_menu():

    print("\n" + "="*70)
    print("MQTT BARRIER SIMULATOR - Independent Test Tool")
    print("="*70)
    print("1. Automatic Simulation (5 predefined scenarios)")
    print("2. Random Simulation (15 commands, 2s interval)")
    print("3. Continuous Simulation (60 seconds)")
    print("4. Vision Detection Simulation (Camera scenarios)")
    print("5. Stress Test (30 seconds, high load)")
    print("6. Pattern Simulation (Repeating pattern, 5 cycles)")
    print("7. Custom Single Command")
    print("8. Custom Random Simulation (Set count & interval)")
    print("0. Exit")
    print("="*70)

def custom_single_command(simulator: MQTTSimulator):

    print("\nCUSTOM COMMAND")
    print("Status: 0=STOP, 1=MOVE")
    print("Direction: 0=LEFT, 1=RIGHT")
    
    try:
        status_val = int(input("Enter status (0/1): "))
        direction_val = int(input("Enter direction (0/1): "))
        
        if status_val not in [0, 1] or direction_val not in [0, 1]:
            logger.error("Invalid values!")
            return
        
        status = StateBarrier(status_val)
        direction = DirectionBarrier(direction_val)
        
        simulator.send_command(status, direction)
        
    except ValueError:
        logger.error("Invalid input!")

def custom_random_simulation(simulator: MQTTSimulator):

    print("\nCUSTOM RANDOM SIMULATION")
    
    try:
        count = int(input("Number of commands (default 15): ") or "15")
        interval = float(input("Interval in seconds (default 2.0): ") or "2.0")
        
        if count <= 0 or interval < 0:
            logger.error("Invalid values!")
            return
        
        random_simulation(simulator, count, interval)
        
    except ValueError:
        logger.error("Invalid input!")




def main():
    """Ana program"""
    
    print("\n" + "="*70)
    print("MQTT BARRIER SIMULATOR STARTING...")
    print("="*70)
    

    simulator = MQTTSimulator()
    

    if not simulator.connect():
        logger.error("Failed to connect to broker")
        return
    

    simulation_thread = ThreadedSimulation(simulator)
    
    try:
        while True:
            show_menu()
            
            try:
                choice = input("\nSelect option (0-8): ").strip()
                
                if choice == '0':
                    logger.info("Exiting simulator...")
                    break
                
                elif choice == '1':
                    simulation_thread.start(automatic_simulation)
                
                elif choice == '2':
                    simulation_thread.start(random_simulation, 15, 2.0)
                
                elif choice == '3':
                    simulation_thread.start(continuous_simulation, 60)
                
                elif choice == '4':
                    simulation_thread.start(vision_simulation)
                
                elif choice == '5':
                    simulation_thread.start(stress_test, 30, 0.5)
                
                elif choice == '6':
                    simulation_thread.start(pattern_simulation, 5)
                
                elif choice == '7':
                    custom_single_command(simulator)
                
                elif choice == '8':
                    custom_random_simulation(simulator)
                
                else:
                    logger.warning("⚠Invalid option!")
                
            except KeyboardInterrupt:
                logger.info("\n⚠Interrupted by user")
                break
                
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    finally:
        simulation_thread.stop()
        simulator.disconnect()
        logger.info("\nSimulator terminated")

if __name__ == "__main__":
    main()
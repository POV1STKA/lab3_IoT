import os

# Configuration for MQTT
MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "mqtt")
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", 1883))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "agent_data_topic")

# Configuration for the Store API
STORE_API_HOST = os.environ.get("STORE_API_HOST", "store_api")
STORE_API_PORT = os.environ.get("STORE_API_PORT", 8000)
STORE_API_BASE_URL = os.environ.get("STORE_API_BASE_URL", f"http://{STORE_API_HOST}:{STORE_API_PORT}")

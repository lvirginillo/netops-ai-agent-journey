# test_connection.py
from dotenv import load_dotenv
import os
from netmiko import ConnectHandler

load_dotenv()

device = {
    "device_type": os.getenv("DEVICE_TYPE"),
    "host":        os.getenv("DEVICE_HOST"),
    "port":        int(os.getenv("DEVICE_PORT", 22)),
    "username":    os.getenv("DEVICE_USER"),
    "password":    os.getenv("DEVICE_PASS"),
}

print(f"Conectando a {device['host']}...")

with ConnectHandler(**device) as conn:
    output = conn.send_command("show version | include IOS")
    print("Conexión OK")
    print(output)

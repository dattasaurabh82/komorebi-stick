from button import Button
from wifi_config.network_manager import NetworkManager
from wifi_config.web_server import run_server, stop_server, server_running
import threading
import time
from logger import logger


# ------------------------------------------- #
# ************* Global Variables ************ #
# ------------------------------------------- #

AP_SELF_IP = "10.10.1.1"
AP_SSID="KOMOREBI-PI-STICK"
WIFI_RESET_PIN = 23

# * Note: From webserver and DNSServer 
server_thread = None
server_running = False


# ------------------------------------------- #
# * Call backl functions for button presses * #
# ------------------------------------------- #

def on_short_press():
    logger.info("[app.py][Event] Short Press detected... Do nothing!")


def on_long_press():
    global server_thread, server_running
    logger.info("")  # For a new line
    logger.info("[app.py][Event] Long Press detected!")
    if server_running:
        logger.info("[app.py][Action] Stopping existing server...")
        stop_server()
        server_thread = None
        server_running = False

    logger.info("[app.py][Action] Setting up Access Point ...")
    NetworkManager.setup_ap()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    logger.info(f"[app.py][Result] Web server started. Connect to the Wi-Fi and navigate to http://{AP_SELF_IP}")


# ------------------------------------------ #
# ******** Create a Button instance ******** #
# ------------------------------------------ #

button = Button(pin=WIFI_RESET_PIN, debounce_time=0.02, long_press_time=4)
# Note: Default Values in the class 
# GPIO pin is 23 
# Debounce time is 10 ms (0.01)
# Long press threshold time period is 5 sec

button.on_short_press = on_short_press
button.on_long_press = on_long_press

# ------------------------------------------ # 

def main():
    global server_thread, server_running
    while True:
        time.sleep(1)
        if not server_running and server_thread and not server_thread.is_alive():
            logger.info("[app.py][Result] Wi-Fi configuration process completed.")
            server_thread = None

        # Check if we need to stop the server after successful connection
        if server_running and NetworkManager.is_connected_to_wifi():
            current_ip = NetworkManager.get_current_ip()
            if current_ip != AP_SELF_IP:
                logger.info("[app.py][Action] Connected to Wi-Fi. Stopping server...")
                stop_server()
                server_thread = None
                server_running = False

# ------------------------------------------ #

logger.info("-----------------------")
logger.info("KOMOREBI SYS VIEW | LOG")
logger.info("-----------------------")
logger.info("Artist: Saurabh Datta")
logger.info("Loc: Berlin, Germany")
logger.info("Date: Sept|2024")
logger.info("-----------------------")


# If wifi connected print IP address. if not type a message below
logger.info(f"[app.py][Status] Current IP: {NetworkManager.get_current_ip()}")
if NetworkManager.get_current_ip() == AP_SELF_IP:
    logger.info(f"[app.py][Status] Connect to wifi access point: {AP_SSID} and go to: http://komorebi.local or http://komorebi.lan to provide 2.5GHz Wifi credentials")
else:
    logger.info("[app.py][Status] To configure wifi, Long Press the Wifi Reset Button for more than 5 sec")
    


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if server_running:
            stop_server()
        logger.info("[app.py][Result] Program stopped")


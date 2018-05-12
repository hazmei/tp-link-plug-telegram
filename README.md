# tp-link-plug-telegram  
### v2 - development

This controls the tp-link smart plugs without going through the Kasa Application.  
It runs on a Raspberry Pi 3 that is on the same network as the smart plugs.  

### Files  
- homeauto.py - required at gateway end (raspberry pi)
- server.py  - required at server end where it handles telegram bot and sends commands to gateway
- sockets.py - socket definition required on both server and gateway end

### Dependencies  
- python3  
- python3-pip  
- [pyHS100](https://github.com/GadgetReactor/pyHS100)  
- python-telegram-bot  
- pycrypto

### Setup  
1. git pull this repository  
2. install required packages:  
    - `sudo apt-get install python3 python3-pip`
    - `pip3 install python-telegram-bot`
    - `pip3 install pycrypto`
3. git clone [pyHS100](https://github.com/GadgetReactor/pyHS100) repository
    - `git clone https://github.com/GadgetReactor/pyHS100.git`
4. go to pyHS100 directory and run the following commands:
    - `pip3 install -r requirements.txt`
    - `python3 setup.py build`
    - `python3 setup.py install`

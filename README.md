# tp-link-plug-telegram  

This is the initial version to controlling the tp-link smart plugs without going through the Kasa Application.  
It runs on a Raspberry Pi 3 that is on the same network as the smart plugs.  

### Dependencies  
- python3  
- python3-pip  
- [pyHS100](https://github.com/GadgetReactor/pyHS100)  
- python-telegram-bot  

### Setup  
1. git pull this repository  
2. install required packages:  
    - `sudo apt-get install python3 python3-pip`
    - `pip3 install python-telegram-bot`
3. git pull pyHS100 repository
4. go to pyHS100 directory and run the following commands:
    - `pip3 install -r requirements.txt`
    - `python3 setup.py build`
    - `python3 setup.py install`

import sys
import re
from luis_sdk import LUISClient

class luis:
    def __init__(self, appid, appkey):
        self.client = LUISClient(appid, appkey, True)

    def query(self, msg):
        response = self.client.predict(msg)

        while response.get_dialog() is not None and not response.get_dialog().is_finished():
            TEXT = input('%s\n'%response.get_dialog().get_prompt())
            response = CLIENT.reply(TEXT, response)

        return response

    def extract_commands(self, response):
        command_dict = {}

        if response.get_top_intent() is "Speech.Greetings":
            # print("This is start")
            command_dict['command'] = 'greetings'
        elif response.get_top_intent() is None or len(response.get_entities()) is 0:
            # print("I don't understand")
            command_dict['command'] = None
        else:
            if len(response.get_entities()) == 1:
                # print((response.get_entities())[0].get_type())
                command_dict['command'] = re.sub(r'.*::','', str((response.get_entities())[0].get_type()))
            elif len(response.get_entities()) == 2:
                command_dict = {'command' : re.sub(r'.*::','', str((response.get_entities())[0].get_type())), 'device' : re.sub(r'.*::','', str((response.get_entities())[1].get_type()))}
            
        # print(command_dict)
        return command_dict


def unit_test():
    appid = '<luis.ai appid>'
    appkey = '<luis.ai appkey>'

    try:
        conversationObj = luis(appid, appkey)

        while True:
            msg = input("\nInput text to predict: ")
            response = conversationObj.query(msg)
            print(conversationObj.extract_commands(response))
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    unit_test()
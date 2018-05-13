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


def process_res(res):
    '''
    A function that processes the luis_response object and prints info from it.
    :param res: A LUISResponse object containing the response data.
    :return: None
    '''
    print('---------------------------------------------')
    print('LUIS Response: ')
    print('Query: ' + res.get_query())
    print('Top Scoring Intent: ' + res.get_top_intent().get_name())
    if res.get_dialog() is not None:
        if res.get_dialog().get_prompt() is None:
            print('Dialog Prompt: None')
        else:
            print('Dialog Prompt: ' + res.get_dialog().get_prompt())
        if res.get_dialog().get_parameter_name() is None:
            print('Dialog Parameter: None')
        else:
            print('Dialog Parameter Name: ' + res.get_dialog().get_parameter_name())
        print('Dialog Status: ' + res.get_dialog().get_status())
    print('Entities:')
    for entity in res.get_entities():
        print('"%s":' % entity.get_name())
        print('Type: %s, Score: %s' % (entity.get_type(), entity.get_score()))


def main():
    try:
        APPID = '0399a616-de56-4d18-8f3b-3c96295784aa'
        APPKEY = 'a5b16542971c4081874aacc4645eb7ec'

        while True:
            TEXT = input("\nInput text to predict: ")
            CLIENT = LUISClient(APPID, APPKEY, True)
            response = CLIENT.predict(TEXT)

            while response.get_dialog() is not None and not response.get_dialog().is_finished():
                TEXT = input('%s\n'%response.get_dialog().get_prompt())
                response = CLIENT.reply(TEXT, response)

            # process_res(response)
            # print("intent predicted: {}".format(response.get_top_intent().get_name()))
            # print("entities: {}".format(response.get_entities()))
            # print("composite_entities: {}".format(response.get_composite_entities()))
            # print("dialog: {}".format(response.get_dialog()))

            print()
            print("entities length: {}".format(len(response.get_entities())))
            command_dict = {}

            if response.get_top_intent() is "Speech.Greetings":
                print("This is start")
                command_dict['command'] = 'greetings'
            elif response.get_top_intent() is None or len(response.get_entities()) is 0:
                print("I don't understand")
                command_dict['command'] = None
            else:
                if len(response.get_entities()) == 1:
                    print((response.get_entities())[0].get_type())
                    command_dict['command'] = re.sub(r'.*::','', str((response.get_entities())[0].get_type()))
                elif len(response.get_entities()) == 2:
                    command_dict = {'command' : re.sub(r'.*::','', str((response.get_entities())[0].get_type())), 'device' : re.sub(r'.*::','', str((response.get_entities())[1].get_type()))}
                
            print(command_dict)
                    # for entities in response.get_entities():
                    #     print("name: {}".format(re.sub(r'.*::','', str(entities.get_type()))))
    except KeyboardInterrupt:
        print()
        sys.exit()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
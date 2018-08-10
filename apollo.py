import requests
import os
import json
import time
import datetime

global old_id
global bot_id
old_id = 1

def main():
    global bot_id
    config = checkConfig()
    bot_id = config[2]

    while True:
        message = getMessage(config[0],config[1])
        print(message.lower())
        message = message.lower().split()

        if message[0] == 'train' or message[0] == 'trains' or message[0] == 'trainz':
            try:
                trainInterpreter(message)
            except Exception:
                sendMessage('Hmmm it seems like you entered something incorrectly.  Try typing "man"')

        elif message[0] == 'stations' or message[0] == 'station' or message[0] == 'stationz':
            print('New Bern  -  East West  -  Bland  -  Carson  -  Stonewall  -  3rd Street  -  ctc')
            sendMessage('New Bern  -  East West  -  Bland  -  Carson  -  Stonewall  -  3rd Street  -  CTC')

        if message[0] == 'man':
            print("https://raw.githubusercontent.com/joshuaberg/apollo/master/README.md")
            sendMessage("https://raw.githubusercontent.com/joshuaberg/apollo/master/README.md")

        time.sleep(5)

#########################################################################################################################

def trainInterpreter(message):

    #Shortcup for NewBern North
    if message[1] == 'home':
        #nextTrains = getTrains('station-19','inbound')
        getTrains('station-8','inbound')
        return

    #Parse Station Names Here
    #stationName = ''.join(message[1:-1])
    #print (stationName)

    #Select a Direction
    if message[-1] == 'north':
        direction = 'inbound'
        station = stationsInbound[''.join(message[1:-1])]

    elif message[-1] == 'south':
        direction = 'outbound'
        station = stationsOutbound[''.join(message[1:-1])]

    getTrains(station,direction)


def getTrains(station,direction):
    #get current time in minutes + current day of the week
    now = datetime.datetime.now()
    h = now.hour
    m = now.minute
    time_min = (h*60) + m
    day = datetime.date.today().weekday()  # 0 is monday   6 is sunday

    #get full train schedule
    config_path = os.path.abspath('schedules.json')
    with open(config_path) as f:
        parsed_json = json.load(f)


    if day == 5: #saturday
        lineup = direction + 'Saturday'
        full_schedule = parsed_json[lineup][station]
    elif day == 6:
        lineup = direction + 'Sunday'
        full_schedule = parsed_json[lineup][station]
    else:
        lineup = direction + 'Weekday'
        full_schedule = parsed_json[lineup][station]

    next3Trains = []
    k = 0
    for arrival in full_schedule:
        #check if thutese value is an actual number, convert it to # if so
        if arrival != 'no stop':
            sch_min = (int(arrival[:2])*60) + int(arrival[-2:]) #converts arival time to min
            #check if ntime is larger then the current time, if so get difference in times
            if sch_min > time_min:
                time_until_train = sch_min - time_min
                #build an array next three values
                if time_until_train > 60:
                    hr = math.floor(time_until_train/60)
                    min = time_until_train - (hr * 60)
                    next3Trains.append("{} hr {} min".format(hr,min))
                else:
                    next3Trains.append("{} min".format(time_until_train))

                k = k + 1
                if k == 3:
                    break
    print(next3Trains)

    schedule_1 = selectScheduleTime(next3Trains,0)
    schedule_2 = selectScheduleTime(next3Trains,1)
    schedule_3 = selectScheduleTime(next3Trains,2)

    sendMessage(    schedule_1 + '  -  ' + schedule_2 + '  -  ' + schedule_3  )


#############################################################################################################################
def selectScheduleTime(array,num):
    try:
        return(array[num])
    except:
        return('none')

#############################################################################################################################

#Check GroupMe for a New Message
def getMessage(token, groupID):
    global old_id
    base_url = 'https://api.groupme.com/v3/groups/' + groupID + '/messages'
    payload = {'token' : token }
    req = requests.get(base_url, params = payload)
    parsed_json = req.json()

    message_id = parsed_json['response']['messages'][0]['id'] #check the message Id

    #if the message is new (IE, not equal to the old message id, get the message and return it)
    if message_id != old_id:
        message = parsed_json['response']['messages'][0]['text']
        old_id = message_id
        return(message)
    else:
        return "None"

###########################################################################################################################
def sendMessage(message):
    global bot_id
    payload = { 'bot_id' : bot_id , 'text': message }
    requests.post('https://api.groupme.com/v3/bots/post', params = payload)


#############################################################################################################################
#check the config file for the GroupMe token and group ID
def checkConfig():
    config_path = os.path.abspath('config.json')
    with open(config_path) as f:
        parsed_json = json.load(f)

    token = parsed_json['config']['access_token']
    group_id = parsed_json['config']['group_id']
    bot_id = parsed_json['config']['bot_id']
    return([token,group_id,bot_id])

##########################################################################################################################


stationsInbound = {}
stationsInbound["newbern"] = 'station-8'
stationsInbound["eastwest"] = 'station-9'
stationsInbound["bland"] = 'station-10'
stationsInbound['carson'] = 'station-11'
stationsInbound['stonewall'] = 'station-12'
stationsInbound['3rdstreet'] = 'station-13'
stationsInbound['ctc'] = 'station-14'

stationsOutbound = {}
stationsOutbound["newbern"] = 'station-19'
stationsOutbound["eastwest"] = 'station-18'
stationsOutbound["bland"] = 'station-17'
stationsOutbound['carson'] = 'station-16'
stationsOutbound['stonewall'] = 'station-15'
stationsOutbound['3rdstreet'] = 'station-14'
stationsOutbound['ctc'] = 'station-13'

##############################################################################################################################
if __name__ == '__main__':
    main()

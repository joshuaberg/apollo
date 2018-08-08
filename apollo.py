import requests
import os
import json
import time
import datetime

global old_id
old_id = 1

def main():
    config = checkConfig()

    while True:
        message = getMessage(config[0],config[1])
        print(message.lower())

        if str.lower(message) == 'apollo':
            next3Trains = getNext3Trains()
            schedule_1 = selectScheduleTime(next3Trains,0)
            schedule_2 = selectScheduleTime(next3Trains,1)
            schedule_3 = selectScheduleTime(next3Trains,2)
            sendMessage(config[2],'General Kenobi')

        time.sleep(5)

#########################################################################################################################

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

################################################################################################################################

def getNext3Trains():
    #get current time in minutes + current day of the week
    now = datetime.datetime.now()
    h = now.hour
    m = now.minute
    time_min = (h*60) + m
    day = datetime.date.today().weekday()  # 0 is monday   6 is sunday


    #get full train schedule
    req = requests.get('https://raw.githubusercontent.com/brandonfancher/charlotte-lightrail/master/src/helpers/schedules.json')
    parsed_json = req.json()

    # get the current weekday's full schedule
    if day == 5:
        full_schedule = parsed_json['outboundSaturday']['station-19']
    elif day == 6:
        full_schedule = parsed_json['outboundSunday']['station-19']
    else:
        full_schedule = parsed_json['outboundWeekday']['station-19']


    #go through schedule and get next 3 trains
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
    return(next3Trains)

#############################################################################################################################
def selectScheduleTime(array,num):
    try:
        return(array[num])
    except:
        return('none')

###########################################################################################################################
def sendMessage(bot_id,message):
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

##############################################################################################################################
if __name__ == '__main__':
    main()

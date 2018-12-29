import json
import time
import random
import datetime
import sys
import os

from groupmebot import GroupMeBot


# Loads config file, which contains the BOT_ID
with open('config.json', 'r') as f:
    print('ok')
    config = json.load(f)

bot = GroupMeBot(config['BOT_ID'])

# A couple commands use random, so set a seed here
random.seed(time.time())



"""
Train Command
    /trains <station> <direction>
"""

@bot.command("/trains")
def trains(args):
    """
    Get the next three train times for the desired
    direction and destination
    """
    if args[0] == "stations":
        response_text = "newbern - eastwest - bland - carson - stonewall - 3rdstreet - ctc"
        bot.post(response_text)

    else:
        try:
            trainParameters = trainInterpreter(args)
            times = getTrains(trainParameters[0],trainParameters[1])
            response_text = times[0] + '  -  ' + times[1] + '  -  ' + times[2]
            bot.post(response_text)
        except Exception:
            pass




"""
Roll command:
    /roll <number> - Roll a dice. Defaults to 6-sided
"""
@bot.command("/roll")
def roll(args):
    """
    Roll a dice, inspired by Google Hangouts. Optional argument to specify how
    many sides.
    """

    dice = 6

    # Attempt to parse if any arguments
    if args:
        try:
            dice = int(args[0])
        except Exception:
            dice = 6

    response_text = "You rolled a %d" % random.randint(1, dice)
    bot.post(response_text)


"""
Help Command:
    /help - Show this help thing
"""
@bot.command("/help")
def help(args):
    """
    Responds with a list of commands
    """

    # List of commands. Joined by a newline and then posted
    commands = [
        "/trains <station> <direction> - get train times",
        "/trains stations - get a list of supported directions",
        "/roll <number> - Roll a dice. Defaults to 6-sided",
        "/help - Show this help thing"
    ]
    bot.post("Here are the available commands:\n" + "\n".join(commands))




def trainInterpreter(args):
    """
    interprets arguments of the trains command
    to get station and direction
    """

    #Shortcup for NewBern North
    if args[0] == 'home':
        direction = 'inbound'
        station = 'station-8'

    #Select a Direction
    if args[-1] == 'north':
        direction = 'inbound'
        station = stationsInbound[''.join(args[0:-1])]
    elif args[-1] == 'south':
        direction = 'outbound'
        station = stationsOutbound[''.join(args[0:-1])]

    return([station,direction])



def getTrains(station,direction):
    """
    returns next 3 train times given station and direction
    """
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

    schedule_1 = selectScheduleTime(next3Trains,0)
    schedule_2 = selectScheduleTime(next3Trains,1)
    schedule_3 = selectScheduleTime(next3Trains,2)

    return([schedule_1,schedule_2,schedule_3])


def selectScheduleTime(array,num):
    """
    returns train time if available
    returns none if not
    """

    try:
        return(array[num])
    except:
        return('none')



stationsInbound = {}
stationsInbound["newbern"] = 'station-8'
stationsInbound["eastwest"] = 'station-9'
stationsInbound["east/west"] = 'station-9'
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





if __name__ == "__main__":
    # Serve forever
    bot.serve(debug=True, port=4000, threaded=True)

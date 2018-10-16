from random import choice

views = {
    'index': 0,
    'current': 0,
    'puzzle': 0,
    'pdf': 0,
    'answer': 0,
    'chat': 0,
    'message': 0,
    'info': 0,
    'registration': 0,
    'resources': 0,
    'previous': 0,
    'old_hunt': 0,
    'account': 0,
    'contact': 0,
    'user_profile': 0,
    'break': 0,
}

MODIFIER = 1000

# Original Values
# index = ['current'] * 7800 + ['info'] * 270 + ['registration'] * 200 + ['resources'] * 90 + ['previous'] * 60 + ['account'] * 10 + ['contact'] * 10 + ['user_profile'] * 10 + ['break'] * 700
# previous = ['old_hunt'] * 150 + ['break'] * 60
# current = ['puzzle'] * 5400 + ['chat'] * 1100 + ['break'] * 7800
# puzzle = ['pdf'] * 625 + ['answer'] * 4688 + ['break'] * 4688
# chat = ['message'] * 45 + ['break'] * 55

index = ['current'] * 780 + ['info'] * 27 + ['registration'] * 20 + ['resources'] * 9 + ['previous'] * 6 + ['account'] * 1 + ['contact'] * 1 + ['user_profile'] * 1 + ['break'] * 70

previous = ['old_hunt'] * 5 + ['break'] * 2

current = ['puzzle'] * 54 + ['chat'] * 11 + ['break'] * 78

puzzle = ['pdf'] * 2 + ['answer'] * 15 + ['break'] * 15

chat = ['message'] * 9 + ['break'] * 11

time_goal = 28800

time = 0


def up_time(amt):
    global time
    time += amt
    if time > time_goal:
        raise Exception('Times up!!')


for i in range(240 * MODIFIER):
    time = 0

    try:
        while True:
            views['index'] += 1
            up_time(30)
            while True:
                r = choice(index)
                views[r] += 1
                if(r == 'current'):
                    up_time(30)
                    while True:
                        r = choice(current)
                        views[r] += 1
                        if(r == 'puzzle'):
                            up_time(30)
                            while True:
                                r = choice(puzzle)
                                views[r] += 1
                                if(r == 'break'):
                                    break
                                else:
                                    up_time(1060)
                        elif(r == 'chat'):
                            up_time(30)
                            while True:
                                r = choice(chat)
                                views[r] += 1
                                if(r == 'break'):
                                    break
                                else:
                                    up_time(160)
                        elif(r == 'break'):
                            break
                        else:
                            up_time(30)
                elif(r == 'previous'):
                    up_time(30)
                    while True:
                        r = choice(previous)
                        views[r] += 1
                        if(r == 'break'):
                            break
                        else:
                            up_time(30)
                elif(r == 'break'):
                    break
                else:
                    up_time(30)
    except:
        pass

for k in views:
    print k + ": " + str(views[k] / MODIFIER)

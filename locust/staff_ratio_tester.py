from random import choice

views = {
    'chat': 0,
    'message': 0,
    'progress': 0,
    'unlock': 0,
    'queue': 0,
    'num_page': 0,
    'respond': 0,
    'email': 0,
    'admin': 0,
    'management': 0,
    'break': 0,
}

MODIFIER = 1000

AVG_WAIT = 120

# Original Values
# base = ['chat'] * 124 + ['progress'] * 136 + ['queue'] * 159 + ['email'] * 39 + ['admin'] * 10 + ['management'] * 30
# chat = ['message'] * 784 + ['break'] * 216
# progress = ['unlock'] * 218 + ['break'] * 782
# queue = ['num_page'] * 103 + ['respond'] * 624 + ['break'] * 273

base = ['chat'] * 15 + ['progress'] * 27 + ['queue'] * 32 + ['email'] * 8 + ['admin'] * 2 + ['management'] * 6
chat = ['message'] * 98 + ['break'] * 27
progress = ['unlock'] * 27 + ['break'] * 98
queue = ['num_page'] * 17 + ['respond'] * 104 + ['break'] * 45

time_goal = 28800

time = 0


def up_time(amt):
    global time
    time += amt
    if time > time_goal:
        raise Exception('Times up!!')


for i in range(10 * MODIFIER):
    time = 0
    try:
        while True:
            r = choice(base)
            views[r] += 1
            if(r == 'chat'):
                up_time(AVG_WAIT)
                while True:
                    r = choice(chat)
                    views[r] += 1
                    if(r == 'break'):
                        break
                    else:
                        up_time(70)
            elif(r == 'progress'):
                up_time(AVG_WAIT)
                while True:
                    r = choice(progress)
                    views[r] += 1
                    if(r == 'break'):
                        break
                    else:
                        up_time(465)
            elif(r == 'queue'):
                up_time(AVG_WAIT)
                while True:
                    r = choice(queue)
                    views[r] += 1
                    if(r == 'break'):
                        break
                    else:
                        up_time(418)
            else:
                up_time(AVG_WAIT)
    except:
        pass

for k in views:
    print k + ": " + str(views[k] / MODIFIER)

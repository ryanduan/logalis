#!/usr/bin/python

import datetime
import random
timenow = str(datetime.datetime.now())
e = timenow+" ERROR\n   sth sth \n sth sth \n"
i = timenow+" INFO sth \n"
w = timenow+" WARNING sth \n"
a = random.randrange(1,10)
b = random.randrange(1,10)
c = random.randrange(1,10)
tif = e*a+i*a+w*a

lf = open("test01.log", 'a')
lf.write(tif)
lf.close()



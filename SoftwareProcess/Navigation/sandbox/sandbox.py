test = '-15.0d'
x = test.partition ('d')
if (not(x[1]=='d')):
    raise ValueError('no d')

print int(x[2])
try:
    a = int(x[0])
    print a
except ValueError:
    print "gg"

a=10.00000
b=round(a,1)
print b

if (a==b):
    print ('true')
else:
    print ('false')
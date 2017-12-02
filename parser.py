o= open("data/cleaned.txt","w+")
f = open('data/Simpsons-Scripts.txt','r')
try:
    while f is not None:
        text = f.readline()
        if 'HOMER' in text:
            g = next(f)
            while(g != '\n'):
                o.write(g)
                g = next(f)
except Exception:
    print(Exception)
finally:
    o.close()
    f.close()
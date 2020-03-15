import sys
from research import research
from test import test

if __name__ == '__main__':
    print("Start")
    mode = "t"
    if len(sys.argv) > 1 and sys.argv[1]:
        mode = sys.argv[1]
    if mode == "t":
        print("Start tests")
        test()
    else:
        print("Start research")
        research()

class abc:
    def __init__(self):
        print "\ninside __init__";

    def callInit(self):
        print "calling __init__ inside callInit method";

    def printLoop(self):
        for i in range(0, 10):
            print "i = %s"%i;
            self.callInit();


var=abc();
var.callInit();
var.printLoop();
var.__init__();



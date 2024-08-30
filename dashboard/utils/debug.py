# Copied from https://stackoverflow.com/questions/34908216/how-to-do-debugging-prints-in-python
import logging
import os
import time


DEBUG = True
LOCAL_DEBUG = True

logging.basicConfig(level=logging.DEBUG)
log=logging.getLogger('=>')    


#DebugPrint.py
#DbgPrint=logging.debug 
def debug_print(*args, **kwargs):
    if DEBUG:
        #get module, class, function, linenumber information
        import inspect
        className = None
        try:
            className = inspect.stack()[2][0].f_locals['self'].__class__.__name__
        except:
            pass
        modName=None
        try:
            modName = os.path.basename(inspect.stack()[2][1])
        except:
            pass
        lineNo=inspect.stack()[2][2]
        fnName=None
        try:
            fnName = inspect.stack()[2][3]
        except:
            pass
        debug_info="line#{}:{}->{}->{}()".format(lineNo, modName,className, fnName)
        argCnt=len(args)
        kwargCnt=len(kwargs)
        fmt=""
        fmt1=debug_info+":"+time.strftime("%H:%M:%S")+"->"
        if argCnt > 0:
            fmt1+=(argCnt-1)*"%s,"
            fmt1+="%s"
            fmt+=fmt1

        if kwargCnt>0:
            fmt2="%s"
            args+=("{}".format(kwargs),)
            if len(fmt)>0:
                fmt+=","+fmt2
            else:
                fmt+=fmt2

        if LOCAL_DEBUG:
            print(kwargs)
        log.debug(fmt,*args)
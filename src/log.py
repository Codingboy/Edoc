import logging

PROJECTNAME = "edoc"
LOGNAME = PROJECTNAME+".log"
fileLogging = False

logger = logging.getLogger(PROJECTNAME)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
if fileLogging:
	fh = logging.FileHandler(LOGNAME)
	fh.setLevel(logging.DEBUG)
	fh.setFormatter(formatter)
	logger.addHandler(fh)

def getLog():
	return logger
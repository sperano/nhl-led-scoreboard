from nhlpy import NHLClient
from utils import args


nhl_Verbose = False
if args().loglevel != None:
    if args().loglevel.lower() == "debug":
        nhl_Verbose = True
    
client = NHLClient(verbose=False,timeout=args().nhl_timeout,ssl_verify=args().nhl_ssl_verify)

from pssh import *

hostlist = ['109.231.122.228' ,'109.231.122.187' ,'109.231.122.173' ,'109.231.122.164' ,'109.231.122.233' ,'109.231.122.201' ,'109.231.122.130' 
,'109.231.122.231' ,'109.231.122.194' ,'109.231.122.182' ,'109.231.122.207' ,'109.231.122.156' ,'109.231.122.240' ,'109.231.122.127']

client = ParallelSSHClient(hostlist, user='ubuntu',password='rexmundi220')
client.copy_file('nodeBootstrapper.sh','nodeBootstrapper.sh')
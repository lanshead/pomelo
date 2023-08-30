import time
import math
from datetime import datetime
print(datetime.fromtimestamp(math.floor(time.time())).strftime("%d-%b-%Y %H:%M:%S"))

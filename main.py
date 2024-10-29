from importing_modules import *

with Client(TOKEN) as client:
    print(client.users.get_accounts())



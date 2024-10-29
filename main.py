from tinkoff.invest import Client

TOKEN = "t.ih1mHMIYiwF-5WqlWftOX-A5FyuKxjAm128C6GO65sdi9s4rFsEHTQL8eOfwdeMSmUU_SNa3rR0zvOabBaRTWA"

with Client(TOKEN) as client:
    print(client.users.get_accounts())



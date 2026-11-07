# Mail migration (draft)

Move mailboxes with tools/mbox.py, then update the routing table in
config/routes.txt to point at the new host. The routing table must
declare format 6 because older formats silently drop exter

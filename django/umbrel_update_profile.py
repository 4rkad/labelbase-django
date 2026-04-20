import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "labellabor.settings")
django.setup()
from userprofile.models import Profile
eh = os.environ.get("UMBREL_ELECTRUM_HOSTNAME")
ep = os.environ.get("UMBREL_ELECTRUM_PORTS", "t50001")
me = os.environ.get("UMBREL_MEMPOOL_ENDPOINT")
if eh:
    n = Profile.objects.filter(electrum_hostname="electrum.emzy.de").update(electrum_hostname=eh, electrum_ports=ep)
    print(f"updated {n} profiles with electrum host {eh}")
if me:
    n = Profile.objects.filter(mempool_endpoint="https://mempool.space").update(mempool_endpoint=me)
    print(f"updated {n} profiles with mempool {me}")

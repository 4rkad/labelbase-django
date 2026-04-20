import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "labellabor.settings")
django.setup()
from userprofile.models import Profile

eh = os.environ.get("UMBREL_ELECTRUM_HOSTNAME")
ep = os.environ.get("UMBREL_ELECTRUM_PORTS", "t50001")
me = os.environ.get("UMBREL_MEMPOOL_ENDPOINT")

# Any hostname the 4rkad Umbrel package has ever shipped as its Electrum default.
ELECTRUM_STALE_HOSTS = (
    "electrum.emzy.de",
    "10.21.21.10",
)
MEMPOOL_STALE_ENDPOINTS = (
    "https://mempool.space",
    "http://10.21.21.26:3006",
)

if eh:
    n = Profile.objects.filter(
        electrum_hostname__in=ELECTRUM_STALE_HOSTS
    ).update(electrum_hostname=eh, electrum_ports=ep)
    print(f"migrated {n} profiles to electrum host {eh}")

if me:
    n = Profile.objects.filter(
        mempool_endpoint__in=MEMPOOL_STALE_ENDPOINTS
    ).update(mempool_endpoint=me)
    print(f"migrated {n} profiles to mempool {me}")

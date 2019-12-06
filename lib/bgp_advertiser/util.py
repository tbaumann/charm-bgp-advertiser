from pyroute2 import IPRoute
from charmhelpers.core.hookenv import log
from charms.layer import status
from charms.reactive import set_flag, clear_flag
REQUIRED_FIELDS = ['vips', 'local_as', 'peer_as', 'router_id', 'neighbors']

def get_neighbours(config):
    # FIXME spaces
    neighbours = []
    with IPRoute() as ipr:
        for neighbour in config['neighbors'].split(','):
            try: # Catch illegal IP and stuff like that
                routes = ipr.route('get', dst=neighbour)
                for route in routes: #Just for safety in case respose is empty or multiple elements
                    attrs = dict(route['attrs'])
                    neighbours.append({
                        'neighbour': neighbour,
                        'local_address': attrs['RTA_PREFSRC']
                    })
            except:
                log("Skipping bad neighbor entry {}".format(neighbour))
                next
    return neighbours

def has_required_fields(config):
    missing_fields = []
    for field in REQUIRED_FIELDS:
        if not config[field]:
            missing_fields.append(field)
    if len(missing_fields) > 0:
        log("Blocked missing options [{}]".format(" ".join(missing_fields)))
        status.blocked("Configuration incomplete. Required fields {}".format(" ".join(missing_fields)))
        set_flag('bgp-advertiser.blocked.options')
        return False
    else:
        clear_flag('bgp-advertiser.blocked.options')
        return True
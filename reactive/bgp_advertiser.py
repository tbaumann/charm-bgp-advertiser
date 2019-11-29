from charms.reactive import when, when_not, set_flag, hook
from charmhelpers.core.hookenv import log, config, service_name
from charms.templating.jinja2 import render
from charms.layer import status
import charms.coordinator

from bgp_advertiser.util import get_neighbours

EXABGP_CONF = '/etc/exabgp/exabgp.conf'


@when_not('bgp-advertiser.ready')
@when('apt.installed.exabgp')
def install_bgp_advertiser():
    # FIXME register service
    set_flag('bgp-advertiser.ready')


@when('bgp-advertiser.ready')
def is_ready():
    # FIXME dislay active node count
    status.active('Ready')


@when('bgp-advertiser.ready')
@when('config.changed')
def write_config():
    context = config()
    context['neighbours'] = get_neighbours()
    context['app_name'] = service_name()
    render('exabgp.conf', EXABGP_CONF, context)
    charms.coordinator.acquire('restart')


@when('coordinator.granted.restart')
def restart():
    status.maintenance('Rolling restart')
    # FIXME restart()
    status.active('Live')


@hook('stop')
def stopped():
    #FIXME Cleanup and disable service
    log("Uninstalling")
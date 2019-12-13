from charms.reactive import when, when_not, set_flag, hook, clear_flag
from charmhelpers.core.hookenv import log, config, service_name
from charmhelpers.core.host import service_start, service_stop, service_restart, service_pause, service_resume, service_running
from charms.templating.jinja2 import render
from charms.layer import status
import charms.coordinator

from bgp_advertiser.util import get_neighbours, has_required_fields

from os.path import exists
import time

EXABGP_CONF = '/etc/exabgp/exabgp.conf'
SERVICENAME = 'exabgp'


@hook('update-status')
@when('bgp-advertiser.running')
def update_status():
    if not service_running(SERVICENAME):
        status.blocked('exabgp service failed')
    elif not exists('/tmp/exabgp-{}.up'.format(service_name())):
        status.active('ready (down)')
    else:
        status.active('ready (up)')


@when_not('bgp-advertiser.ready')
@when('apt.installed.exabgp')
def install_bgp_advertiser():
    # FIXME Do we even need this post-inst step?
    set_flag('bgp-advertiser.ready')
    write_config()


@when('bgp-advertiser.ready')
@when('bgp-advertiser.running')
def is_ready():
    update_status()


@when('bgp-advertiser.should-run')
@when_not('bgp-advertiser.running')
def start_service():
    log("Starting exabgp service")
    service_resume(SERVICENAME)
    service_start(SERVICENAME)
    set_flag('bgp-advertiser.running')


@when_not('bgp-advertiser.should-run')
@when('bgp-advertiser.running')
def stop_service():
    log("Stopping exabgp service")
    service_pause(SERVICENAME)
    service_stop(SERVICENAME)
    clear_flag('bgp-advertiser.running')


@when('bgp-advertiser.ready')
@when('config.changed')
def write_config():
    context = config()
    if has_required_fields(context):
        context['neighbours'] = get_neighbours(context)
        context['app_name'] = service_name()
        log("VIP={}".format(context['vips']))
        render('exabgp.conf', EXABGP_CONF, context)
        set_flag('bgp-advertiser.should-run')
        charms.coordinator.acquire('restart')
    else:
        clear_flag('bgp-advertiser.should-run')


@when('coordinator.granted.restart')
def restart():
    status.maintenance('Rolling restart')
    service_restart(SERVICENAME)
    #FIXME wait for service advertisment
    time.sleep( 30 )
    update_status()


@hook('stop')
def stopped():
    log("Uninstalling")
    clear_flag('bgp-advertiser.should-run')

@hook('upgrade-charm')
def upgrade_charm():
    write_config()


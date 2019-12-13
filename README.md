# Overview

This charm is used to advertise virtual IP of scaled services via BGP.

The use case is for router fabric based HA.

The service to be exported can be monitred via a healthcheck command.
The route is withdrawn if the servie is unavailable.

# Usage

`juju deploy bgp-advertiser apache-vip`

`juju config apache-vip ...`

`juju relate apache-vip apache`



## Scale out Usage

Scale out the principal unit this is related to.


## Known Limitations and Issues

Currently only one instance of this charm can be deployed per machine


## Upstream Project Name

  - website https://github.com/tbaumann/charm-bgp-advertiser
  - bug tracker https://github.com/tbaumann/charm-bgp-advertiser/issues

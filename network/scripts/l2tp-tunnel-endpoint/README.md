# l2tp-update.sh

This script (re)creates L2TP tunnels based on a list of endpoints. Useful when dealing with dynamic end points by using DDNS to compare existing IP address with DNS resolved IP address.

## Usage
Script should be run via `cron` at regular intervals:

Example
```
*/5 *  * * *   root    /usr/local/bin/l2tp-update.sh > /dev/null
```
## Configuration

Script uses `/etc/l2tp.list` to build and update the tunnels.

Format:

`0 000.000.000.000 XXXX`

`0` - Index number from 0-63. This will inform the interface number and P2P subnet that will be generated
`000.000.000.000` - IP address of FQDN of remote endpoint of tunnel
`XXXX` - SINGLE WORD comment about the tunnel. Not used anywhere but for reference
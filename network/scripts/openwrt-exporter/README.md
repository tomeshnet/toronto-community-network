# Install on OpenWRT

## Create HTTPD instance on port 9100 pointing to folder /www2
```
mkdir /www2
uci set uhttpd.node=uhttpd
uci set uhttpd.node.listen_http='0.0.0.0:9100'
uci set uhttpd.node.home='/www2'
uci set uhttpd.node.rfc1918_filter='1'
uci set uhttpd.node.max_requests='3'
uci set uhttpd.node.max_connections='100'
uci set uhttpd.node.script_timeout='60'
uci set uhttpd.node.network_timeout='30'
uci set uhttpd.node.http_keepalive='20'
uci set uhttpd.node.tcp_keepalive='1'
uci set uhttpd.node.cgi_prefix='/metrics'
uci commit
/etc/init.d/uhttpd restart
```

## Place file in /www2/metrics

`wget ...../metrics`

## Mark executable
````
chmod +x /www2/metrics
```

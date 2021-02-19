#!/bin/bash

# IP Address of node
MYIP=199.195.250.209
EXITINDEX=0
# TCP Port babeld has write access (-G)
BABELDPORT=999

# Get babeld data
#exec 3<>/dev/tcp/::/$BABELDPORT
#echo "dump" 1>&3
#echo "quit" 1>&3
#response="$(cat <&3)"
#exec 3<&-

while read -r INDEX CLIENTIP NOTE; do
    # Resolves CLIENTIP to IP
    CLIENTIP_DNS=$(getent hosts "$CLIENTIP" | awk '{print $1}')
    if ! [ -z $CLIENTIP_DNS ]; then
        CLIENTIP=$CLIENTIP_DNS
    fi
    # Define tunnel details based on index
    INT=l2tpeth$INDEX
    IP=$((INDEX * 4 + 1))
    EI=$((2 + EXITINDEX))
    EI6=$((32514 + EXITINDEX))
    EI6=$(printf '%x' $EI6)
    IPv4=100.127.$EI.$IP/30
    IPv6=fd74:6f6d:7368:$EI6::$(printf '%x' $IP)/126

    # check to see if there is a created tunnel with the correct ip address already in shste
    if [[ "$CLIENTIP" == "$(ip l2tp show tunnel | grep -A4 "Tunnel $((10000 + INDEX))" | grep From | awk '{print $4}')" ]]; then
        echo ""
    else
        # Delete old tunnel
        ip l2tp delete tunnel tunnel_id $((10000 + INDEX))
        # Let tunnel deletion Settle
        sleep 2
        # Create Tunnel
        ip l2tp add tunnel tunnel_id $((10000 + INDEX)) peer_tunnel_id $((40000 + INDEX)) encap udp local "$MYIP" remote "$CLIENTIP" udp_sport $((10000 + INDEX)) udp_dport $((40000 + INDEX))
        ip l2tp add session name "$INT" tunnel_id $((10000 + INDEX)) session_id $((10000 + INDEX)) peer_session_id $((40000 + INDEX))
        ip link set "$INT" up mtu 1412
        ip addr add dev "$INT" "$IPv4"
        ip addr add dev "$INT" "$IPv6"
        # Add interface to babeld so restart is not needed
        exec 3<>/dev/tcp/::/$BABELDPORT
        echo "interface $INT" 1>&3
        echo "redistribute if $INT allow" 1>&3
        exec 3<&-

    fi
done </etc/l2tp.list # list to read

#!/usr/bin/env sh

cat > /tmp/commands.txt <<EOF
deletetable MatsuLevel2LngLat
bye
EOF

~/apps/accumulo-1.3.5/bin/accumulo shell -u root -p password -fv /tmp/commands.txt

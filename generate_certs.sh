#!/bin/bash

country=""
state="" # or province
locality="" # eg, city
organization="" # eg, compnay
organizational_unit="" # eg, section
commonname="" # e.g. server FQDN or YOUR name
email=""

echo -e "$country\n$state\n$locality\n$organization\n$organizational_unit\n$commonname\n$email\n\n\n" | openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes
echo ""
echo "Done."
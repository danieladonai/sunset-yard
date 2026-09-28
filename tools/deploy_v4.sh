#!/bin/bash
# Deploy the working game to https://cy.someantics.xyz/sunset-yard/v4/ (served by the existing public
# /sunset-yard nginx location; no nginx change). v3 stays untouched next to it.
set -e
cd "$(dirname "$0")/.."
D=/var/www/html/sunset-yard/v4
ssh droplet "mkdir -p $D/sunset-yard-assets"
scp -q sunset-yard-assets/*.png sunset-yard-assets/*.jpg droplet:$D/sunset-yard-assets/ 2>/dev/null || true
scp -q -r sunset-yard-assets/chars droplet:$D/sunset-yard-assets/
scp -q sunset-yard-3d.html droplet:$D/index.html
curl -s -o /dev/null -w "v4 %{http_code}\n" https://cy.someantics.xyz/sunset-yard/v4/

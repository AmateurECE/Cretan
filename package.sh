#!/bin/sh
###############################################################################
# NAME:             package.sh
#
# AUTHOR:           Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:      This shell script generates the package files for
#                   distribution
#
# CREATED:          06/01/2020
#
# LAST EDITED:      06/02/2020
###

python3 setup.py sdist

cat - > index.html <<EOF
<!doctype html>
<html>
  <body>
EOF

DIRECTORIES="cretan.egg-info dist"
for dir in $DIRECTORIES; do
    for f in `find $dir -type f`; do
        printf '    <a href="%s">%s</a>\n' "$f" "$f" >> index.html
    done
done

cat - >> index.html <<EOF
  </body>
</html>
EOF

rsync -rvz --progress -e 'ssh -p 5000' $DIRECTORIES index.html \
      edtwardy@edtwardy.hopto.org:/var/www/edtwardy.hopto.org/pypi/cretan/

###############################################################################

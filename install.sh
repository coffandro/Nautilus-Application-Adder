#!/bin/bash

usage() {
cat << EOF
Usage: Nautilus Application Adder [OPTION]...

OPTIONS:
  -i, --install,         Install Nautilus Application Adder, will kill
  -r, --remove,          Remove installed themes
  -c, --clean,           Clean this directory after install

  -h, --help              Show help
EOF
}

install() {
mkdir -p ~/.local/share/nautilus-python/extensions/NautilusApplications
cp Extension/NautilusApplications.py ~/.local/share/nautilus-python/extensions/NautilusApplications
cp Extension/NautliusApplications-runner.py ~/.local/share/nautilus-python/extensions

ConfigFile="$HOME/.local/share/nautilus-python/extensions/NautilusApplications/config.json"
if [ -e $ConfigFile ]; then
    echo "Config exists, removing"
    rm $ConfigFile
fi

touch $ConfigFile
echo '{' >> $ConfigFile
echo '    "items": {' >> $ConfigFile
echo '        "_comment": "Items to include in the context menu",' >>  $ConfigFile
echo '        "AddToLocal": true' >> $ConfigFile
echo '    }' >> $ConfigFile
echo '}' >> $ConfigFile
}

remove() {
rm -r ~/.local/share/nautilus-python/extensions/NautilusApplications
rm ~/.local/share/nautilus-python/extensions/NautliusApplications-runner.py
}

VALID_ARGS=$(getopt -o hir --long help,install,remove -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi

eval set -- "$VALID_ARGS"
while [ : ]; do
  case "$1" in
    -h | --help)
        usage
        shift
        ;;
    -i | --install)
        install
        shift
        ;;
    -r | --remove)
        remove
        shift
        ;;
    --) shift;
        break
        ;;
  esac
done

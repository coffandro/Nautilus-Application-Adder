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
InstallDeps
mkdir -p ~/.local/share/nautilus-python/extensions/NautilusApplications
cp Extension/NautilusApplications.py ~/.local/share/nautilus-python/extensions/NautilusApplications
cp Extension/window.py ~/.local/share/nautilus-python/extensions/NautilusApplications
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
echo '        "AddToLocal": true,' >> $ConfigFile
echo '        "RemoveFromLocal": true' >> $ConfigFile
echo '    }' >> $ConfigFile
echo '}' >> $ConfigFile
}

InstallDeps() {
# Install python-nautilus
echo "Installing python-nautilus..."
if type "pacman" > /dev/null 2>&1
then
    # check if already install, else install
    pacman -Qi python-nautilus &> /dev/null
    if [ `echo $?` -eq 1 ]
    then
        sudo pacman -S --noconfirm python-nautilus
    else
        echo "python-nautilus is already installed"
    fi
elif type "apt-get" > /dev/null 2>&1
then
    # Find Ubuntu python-nautilus package
    package_name="python-nautilus"
    found_package=$(apt-cache search --names-only $package_name)
    if [ -z "$found_package" ]
    then
        package_name="python3-nautilus"
    fi

    # Check if the package needs to be installed and install it
    installed=$(apt list --installed $package_name -qq 2> /dev/null)
    if [ -z "$installed" ]
    then
        sudo apt-get install -y $package_name
    else
        echo "$package_name is already installed."
    fi
elif type "dnf" > /dev/null 2>&1
then
    installed=`dnf list --installed nautilus-python 2> /dev/null`
    if [ -z "$installed" ]
    then
        sudo dnf install -y nautilus-python
    else
        echo "nautilus-python is already installed."
    fi
else
    echo "Failed to find python-nautilus, please install it manually."
fi
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

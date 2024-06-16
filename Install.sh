pkill -f Nautilus

mkdir -p ~/.local/share/nautilus-python/extensions/NautilusApplications
cp Extension/config.json ~/.local/share/nautilus-python/extensions/NautilusApplications
cp Extension/NautilusApplications.py ~/.local/share/nautilus-python/extensions/NautilusApplications
cp Extension/NautliusApplications-runner.py ~/.local/share/nautilus-python/extensions
nautilus

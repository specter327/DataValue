echo "[*] Uninstalling Python library: datavalue...";
pip uninstall datavalue --break-system-packages -y;

echo "[#] Waiting 10 seconds...";
sleep 10;

echo "[*] Installing Python library: datavalue...";
pip install datavalue --break-system-packages;
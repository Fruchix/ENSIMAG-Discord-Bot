
## Setup environment

### Python
```bash
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Firefox
```bash
sudo install -d -m 0755 /etc/apt/keyrings
wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | sudo tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null
gpg -n -q --import --import-options import-show /etc/apt/keyrings/packages.mozilla.org.asc | awk '/pub/{getline; gsub(/^ +| +$/,""); if($0 == "35BAA0B33E9EB396F59CA838C0BA5CE6DC6315A3") print "\nThe key fingerprint matches ("$0").\n"; else print "\nVerification failed: the fingerprint ("$0") does not match the expected one.\n"}'
echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | sudo tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null

echo '
Package: *
Pin: origin packages.mozilla.org
Pin-Priority: 1000
' | sudo tee /etc/apt/preferences.d/mozilla

sudo apt-get update && sudo apt-get install firefox
```

### FirefoxDriver

```bash
latest_release=$(wget -qO- https://api.github.com/repos/mozilla/geckodriver/releases/latest)
latest_version=$(echo "${latest_release}" | grep "tag_name" | cut -d\" -f4 | tr -d v)

ARCH_VERSION="linux64.tar.gz" # get a static version of bat (musl)
ARCHIVE="geckodriver-v${latest_version}-${ARCH_VERSION}"

wget -O "${ARCHIVE}" "https://github.com/mozilla/geckodriver/releases/download/v${latest_version}/${ARCHIVE}"
tar -xvf "${ARCHIVE}"
rm "${ARCHIVE}"
```

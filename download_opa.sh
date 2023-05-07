uname_os() {
	os=$(uname -s | tr '[:upper:]' '[:lower:]')
	case "$os" in
	cygwin_nt*) os="windows" ;;
	mingw*) os="windows" ;;
	msys_nt*) os="windows" ;;
	esac
	echo "$os"
}

uname_arch() {
	arch=$(uname -m)
	case $arch in
	x86_64) arch="amd64" ;;
	x86) arch="386" ;;
	i686) arch="386" ;;
	i386) arch="386" ;;
	aarch64) arch="arm64" ;;
	armv5*) arch="armv5" ;;
	armv6*) arch="armv6" ;;
	armv7*) arch="armv7" ;;
	esac
	echo ${arch}
}

OPA_VERSION="v0.44.0"
OS=$(uname_os)
ARCH=$(uname_arch)
PLATFORM="${OS}_${ARCH}"
DOWNLOAD_URL="https://openpolicyagent.org/downloads/${OPA_VERSION}/opa_${PLATFORM}_static"

echo $PLATFORM $DOWNLOAD_URL

curl -L -o opa $DOWNLOAD_URL
chmod +x opa
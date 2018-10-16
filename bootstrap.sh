#!/bin/bash
	
# Get super user privileges
if [[ $EUID != 0 ]]; then
  export wasnt_root=true
  sudo -E "$0" "$@"
fi

if [[ $EUID == 0 ]]; then
  echo "[$EUID] |>>| installing distro packages"
  apt update
  apt install --no-install-recommends -y git build-essential wget python3-pip curl python3-setuptools autoconf \
    automake libtool unzip pkg-config ca-certificates nasm sudo

  invalid_cmake_version=false
  if command -v cmake > /dev/null ; then 
    cmake_version=`cmake --version | grep -o -E "([0-9]{1,}\.)+[0-9]{1,}"`
    cmake_version=(`echo $cmake_version | tr . ' '`)
    if [ ${cmake_version[1]} -lt 10 ]; then
      echo "[$EUID] |>>| cmake 3.10+ required"
      invalid_cmake_version=true
    fi;
  fi

  if [[ -z `command -v cmake` ]] || [[ $invalid_cmake_version == true ]]; then
    echo "[$EUID] |>>| installing cmake..."; 
    wget https://cmake.org/files/v3.11/cmake-3.11.1-Linux-x86_64.sh
    mkdir -p /opt/cmake
    sh cmake-3.11.1-Linux-x86_64.sh --skip-license --prefix=/opt/cmake
    ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
    rm cmake-3.11.1-Linux-x86_64.sh
  fi

  if ! command -v ninja > /dev/null; then 
    echo "[$EUID] |>>| installing ninja..."; 
    wget https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-linux.zip
    unzip ninja-linux.zip
    rm ninja-linux.zip
    mv ninja /usr/bin
  fi

  pip3 install conan --upgrade
fi

if [[ $EUID != 0 || -z ${wasnt_root} ]]; then
  if ! conan remote list | grep -q "bincrafters:"; then
    echo "[$EUID] |>>| Adding 'bincrafters' remote"; 
    conan remote add bincrafters https://api.bintray.com/conan/bincrafters/public-conan
  fi

  if ! conan remote list | grep -q "is:"; then
    echo "[$EUID] |>>| Adding 'is' remote"; 
    conan remote add is https://api.bintray.com/conan/labviros/is
  fi
fi
#!/bin/bash

#/**
# * @file run.net.sh
# * @dotnet version 
# * @brief just start WebGrab+Plus
# * @based on run.sh from author Francis De Paemeleere
# * @date 31/07/2016
# * @author Jan van Straaten
# * @update date 14/09/2023
# * @loads a custom openssl.cng before running
# */

#backup the current working dir
WG_BCKP_DIR="$(pwd)"

function quit {
    #restore previous working dir
    cd "$WG_BCKP_DIR"
    exit $1;
}

# check if dotnet can be found

which dotnet >/dev/null 2>&1 || { echo >&2 "DotNet required, but it's not installed."; quit 1; }

# get the absolute path of the link (or relative path)
if [ -L $0 ] ; then
    DIR=$(dirname $(readlink -f $0)) ;
else
    DUTDIR=$(dirname $0) ;
    if [ "${DUTDIR:0:1}" = "/" ]; then
        DIR="$DUTDIR";
    else
        DIR=$PWD/$(dirname $0) ;
    fi
fi ;

# load custom openssl.cnf
export OPENSSL_CONF="$DIR/bin.net/openssl.cnf"
dotnet "$DIR/bin.net/WebGrab+Plus.dll" "$DIR"
quit 0;


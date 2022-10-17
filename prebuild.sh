#!/bin/bash -xe

if [[ $DIST == el7 ]]; then
    # EPEL7: libuv-devel
    build_dl "https://dl.fedoraproject.org/pub/epel/epel-release-latest-$DIST_VERSION.noarch.rpm"
    rpm -Uvh "$CACHEDIR/epel-release-latest-$DIST_VERSION.noarch.rpm"
fi

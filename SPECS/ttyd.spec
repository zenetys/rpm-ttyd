%define libwebsockets_version 4.3.3
%define libwebsockets_xprefix libwebsockets-%{libwebsockets_version}

%if 0%{?rhel} == 7
# find-debuginfo.sh fails on el7
%define debug_package %{nil}
%endif

Name: ttyd
Summary: Share your terminal over the web
Version: 1.7.4
Release: 2%{?dist}.zenetys
License: MIT
URL: https://github.com/tsl0922/ttyd

Source0: https://github.com/tsl0922/ttyd/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1: ttyd.service.sample
Source2: ttyd-alt-index.html
Source100: https://github.com/warmcat/libwebsockets/archive/refs/tags/v%{libwebsockets_version}.tar.gz#/%{libwebsockets_xprefix}.tar.gz

Patch100: ttyd-1.7.4-manpage-writable-shortopt.patch

BuildRequires: cmake
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: json-c-devel
BuildRequires: libuv-devel
BuildRequires: openssl-devel
BuildRequires: zlib-devel

%description
ttyd is a simple command-line tool for sharing terminal over the web.

%prep
# ttyd
%setup -n %{name}-%{version}
%patch100 -p1
sed -i -e 's,find_package(Libwebsockets,#\0,' CMakeLists.txt

# libwebsockets
%setup -n %{name}-%{version} -T -D -a 100

%build
libuv_include=%{_includedir}
libuv_lib=%{_libdir}/libuv.so

# libwebsockets
cd %{libwebsockets_xprefix}
mkdir build
cd build
cmake .. \
    -DCMAKE_C_FLAGS="%{?build_cflags:%{build_cflags}} -g" \
    -DCMAKE_EXE_LINKER_FLAGS='-static' \
    -DCMAKE_VERBOSE_MAKEFILE=ON \
    -DLWS_WITHOUT_TESTAPPS=ON \
    -DLWS_WITH_MBEDTLS=OFF \
    -DLWS_WITH_LIBUV=ON \
    -DLWS_LIBUV_INCLUDE_DIRS="$libuv_include" \
    -DLWS_LIBUV_LIBRARIES="$libuv_lib" \
    -DLWS_STATIC_PIC=ON \
    -DLWS_WITH_SHARED=OFF \
    -DLWS_UNIX_SOCK=ON \
    -DLWS_IPV6=ON \
    -DLWS_ROLE_RAW_FILE=OFF \
    -DLWS_WITH_HTTP2=OFF \
    -DLWS_WITH_HTTP_BASIC_AUTH=OFF \
    -DLWS_WITH_UDP=OFF \
    -DLWS_WITHOUT_CLIENT=ON \
    -DLWS_WITHOUT_EXTENSIONS=OFF \
    -DLWS_WITH_LEJP=OFF \
    -DLWS_WITH_LEJP_CONF=OFF \
    -DLWS_WITH_LWSAC=OFF \
    -DLWS_WITH_SEQUENCER=OFF \

make %{?_smp_mflags}
libwebsockets_include=$PWD/include
libwebsockets_lib=$PWD/lib/libwebsockets.a
cd ../..

# ttyd
cmake \
    -DCMAKE_C_FLAGS="%{?build_cflags:%{build_cflags}} -g" \
    -DCMAKE_VERBOSE_MAKEFILE=ON \
    -DCMAKE_INSTALL_BINDIR=%{_bindir} \
    -DCMAKE_INSTALL_MANDIR=%{_mandir} \
    -DLWS_WITH_LIBUV=ON \
    -DLIBUV_INCLUDE_DIR="$libuv_include" \
    -DLIBUV_LIBRARY="$libuv_lib" \
    -DLIBWEBSOCKETS_INCLUDE_DIRS="$libwebsockets_include" \
    -DLIBWEBSOCKETS_LIBRARIES="$libwebsockets_lib"
cmake --build . -- %{?_smp_mflags}

%install
%if 0%{?rhel} >= 8
DESTDIR=%{buildroot} cmake --install .
%else
make install DESTDIR=%{buildroot}
%endif

install -d -m 0755 %{buildroot}%{_datadir}/%{name}
install -D -p -m 0644 -t %{buildroot}%{_datadir}/%{name}/ %{SOURCE1}
install -D -p -m 0644 -t %{buildroot}%{_datadir}/%{name}/ %{SOURCE2}

%files
%license LICENSE
%doc README.md
%{_bindir}/ttyd
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/ttyd.service.sample
%{_datadir}/%{name}/ttyd-alt-index.html
%{_mandir}/man1/ttyd.1.*

%global  _hardened_build     1
%global  nginx_user          nginx

%global  nginx_version       1.12.2
%global  nginx_release       3

%global  module_name         nginx-mod-http-unchunk
%global  module_version      0.1.1

# gperftools exist only on selected arches
%ifnarch s390 s390x
%global with_gperftools 1
%endif

%global with_aio 1

Name:              nginx-mod-http-unchunk
Epoch:             1
Version:           %{nginx_version}.%{module_version}          
Release:           1%{?dist}

Summary:           NGINX HTTP unchunk module
Group:             System Environment/Daemons
License:           BSD
URL:               https://github.com/andantissimo/nginx-mod-http-unchunk

Source0:           http://nginx.org/download/nginx-%{nginx_version}.tar.gz
Source100:         %{module_name}-%{module_version}.tar.gz

# removes -Werror in upstream build scripts.  -Werror conflicts with
# -D_FORTIFY_SOURCE=2 causing warnings to turn into errors.
Patch0:            nginx-auto-cc-gcc.patch

%if 0%{?with_gperftools}
BuildRequires:     gperftools-devel
%endif
BuildRequires:     openssl-devel
BuildRequires:     pcre-devel
BuildRequires:     zlib-devel

Requires:          nginx = %{epoch}:%{nginx_version}-%{nginx_release}%{?dist}

%description
%{summary}.


%prep
%setup -qcTn %{name}-%{version}
tar --strip-components=1 -xf %{SOURCE0}

%patch0 -p0

tar xf %{SOURCE100}


%build
# nginx does not utilize a standard configure script.  It has its own
# and the standard configure options cause the nginx configure script
# to error out.  This is is also the reason for the DESTDIR environment
# variable.
export DESTDIR=%{buildroot}
./configure \
    --prefix=%{_datadir}/nginx \
    --sbin-path=%{_sbindir}/nginx \
    --modules-path=%{_libdir}/nginx/modules \
    --conf-path=%{_sysconfdir}/nginx/nginx.conf \
    --error-log-path=%{_localstatedir}/log/nginx/error.log \
    --http-log-path=%{_localstatedir}/log/nginx/access.log \
    --http-client-body-temp-path=%{_localstatedir}/lib/nginx/tmp/client_body \
    --http-proxy-temp-path=%{_localstatedir}/lib/nginx/tmp/proxy \
    --http-fastcgi-temp-path=%{_localstatedir}/lib/nginx/tmp/fastcgi \
    --http-uwsgi-temp-path=%{_localstatedir}/lib/nginx/tmp/uwsgi \
    --http-scgi-temp-path=%{_localstatedir}/lib/nginx/tmp/scgi \
    --pid-path=/run/nginx.pid \
    --lock-path=/run/lock/subsys/nginx \
    --user=%{nginx_user} \
    --group=%{nginx_user} \
%if 0%{?with_aio}
    --with-file-aio \
%endif
    --with-ipv6 \
    --with-http_auth_request_module \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_degradation_module \
    --with-http_slice_module \
    --with-http_stub_status_module \
    --with-mail_ssl_module \
    --with-pcre \
    --with-pcre-jit \
    --with-stream_ssl_module \
    --add-dynamic-module=%{module_name}-%{module_version} \
%if 0%{?with_gperftools}
    --with-google_perftools_module \
%endif
    --with-debug \
    --with-cc-opt="%{optflags} $(pcre-config --cflags)" \
    --with-ld-opt="$RPM_LD_FLAGS -Wl,-E" # so the perl module finds its symbols

make %{?_smp_mflags} modules

%install
cd %{_builddir}/%{name}-%{version}

install -p -d -m 0755 %{buildroot}%{_libdir}/nginx/modules
install -p -d -m 0755 %{buildroot}%{_datadir}/nginx/modules
install -p -d -m 0755 %{buildroot}%{_datadir}/doc/%{name}-%{version}

install -m 0755 objs/ngx_http_unchunk_module.so %{buildroot}%{_libdir}/nginx/modules/
echo 'load_module "%{_libdir}/nginx/modules/ngx_http_unchunk_module.so";' \
    > %{buildroot}%{_datadir}/nginx/modules/mod-http-unchunk.conf

for doc in LICENSE README.md; do
    install -m 0644 %{module_name}-%{module_version}/$doc \
        %{buildroot}%{_datadir}/doc/%{name}-%{version}
done


%post
if [ $1 -eq 1 ]; then
    /usr/bin/systemctl reload nginx.service >/dev/null 2>&1 || :
fi


%files
%{_libdir}/nginx/modules/*
%{_datadir}/nginx/modules/*
%{_datadir}/doc/%{name}-%{version}


%changelog
* Sat Oct 05 2019 MALU <contact@andantissimo.jp> - 0.1.0-1
- Release

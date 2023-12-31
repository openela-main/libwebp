%global _hardened_build 1

Name:          libwebp
Version:       1.0.0
Release:       8%{?dist}.1
URL:           http://webmproject.org/
Summary:       Library and tools for the WebP graphics format
# Additional IPR is licensed as well. See PATENTS file for details
License:       BSD
Source0:       http://downloads.webmproject.org/releases/webp/%{name}-%{version}.tar.gz
Source1:       libwebp_jni_example.java
Patch0:        rhbz-1956829.patch
Patch1:        rhbz-1956843.patch
Patch2:        rhbz-1956919.patch
Patch3:        rhbz-1956853.patch
Patch4:        rhbz-1956856.patch
Patch5:        rhbz-1956917.patch
Patch6:        rhbz-1956868.patch
Patch7:        mozilla-1819244.patch
Patch8:        4619a48fc-1.0.0.patch

BuildRequires: libjpeg-devel
BuildRequires: libpng-devel
BuildRequires: giflib-devel
BuildRequires: libtiff-devel
BuildRequires: java-devel
BuildRequires: jpackage-utils
BuildRequires: swig
BuildRequires: autoconf automake libtool
BuildRequires: freeglut-devel

%description
WebP is an image format that does lossy compression of digital
photographic images. WebP consists of a codec based on VP8, and a
container based on RIFF. Webmasters, web developers and browser
developers can use WebP to compress, archive and distribute digital
images more efficiently.


%package tools
Summary:       The WebP command line tools
Requires:      %{name}%{?_isa} = %{version}-%{release}

%description tools
WebP is an image format that does lossy compression of digital
photographic images. WebP consists of a codec based on VP8, and a
container based on RIFF. Webmasters, web developers and browser
developers can use WebP to compress, archive and distribute digital
images more efficiently.


%package devel
Summary:       Development files for libwebp, a library for the WebP format
Requires:      %{name}%{?_isa} = %{version}-%{release}

%description devel
WebP is an image format that does lossy compression of digital
photographic images. WebP consists of a codec based on VP8, and a
container based on RIFF. Webmasters, web developers and browser
developers can use WebP to compress, archive and distribute digital
images more efficiently.


%package java
Summary:       Java bindings for libwebp, a library for the WebP format
Requires:      %{name}%{?_isa} = %{version}-%{release}
Requires:      java-headless
Requires:      jpackage-utils

%description java
Java bindings for libwebp.


%prep
%autosetup -p1


%build
autoreconf -vif
%ifarch aarch64
export CFLAGS="%{optflags} -frename-registers"
%endif
# Neon disabled due to resulting CFLAGS conflict resulting in
# inlining failed in call to always_inline '[...]': target specific option mismatch
%configure --disable-static --enable-libwebpmux \
           --enable-libwebpdemux --enable-libwebpdecoder \
           --disable-neon
%make_build V=1

# swig generated Java bindings
cp %{SOURCE1} .
cd swig
rm -rf libwebp.jar libwebp_java_wrap.c
mkdir -p java/com/google/webp
swig -ignoremissing -I../src -java \
    -package com.google.webp  \
    -outdir java/com/google/webp \
    -o libwebp_java_wrap.c libwebp.swig

gcc %{__global_ldflags} %{optflags} -shared \
    -I/usr/lib/jvm/java/include \
    -I/usr/lib/jvm/java/include/linux \
    -I../src \
    -L../src/.libs -lwebp libwebp_java_wrap.c \
    -o libwebp_jni.so

cd java
javac com/google/webp/libwebp.java
jar cvf ../libwebp.jar com/google/webp/*.class


%install
%make_install
find "%{buildroot}/%{_libdir}" -type f -name "*.la" -delete

# swig generated Java bindings
mkdir -p %{buildroot}/%{_libdir}/%{name}-java
cp swig/*.jar swig/*.so %{buildroot}/%{_libdir}/%{name}-java/


%ldconfig_scriptlets


%files tools
%{_bindir}/cwebp
%{_bindir}/dwebp
%{_bindir}/gif2webp
%{_bindir}/img2webp
%{_bindir}/webpinfo
%{_bindir}/webpmux
%{_bindir}/vwebp
%{_mandir}/man*/*

%files -n %{name}
%doc README PATENTS NEWS AUTHORS
%license COPYING
%{_libdir}/%{name}.so.7*
%{_libdir}/%{name}decoder.so.3*
%{_libdir}/%{name}demux.so.2*
%{_libdir}/%{name}mux.so.3*

%files devel
%{_libdir}/%{name}*.so
%{_includedir}/*
%{_libdir}/pkgconfig/*

%files java
%doc libwebp_jni_example.java
%{_libdir}/%{name}-java/


%changelog
* Fri Sep 15 2023 Tomas Popela <tpopela@redhat.com> - 1.0.0-8.el8_8.1
- Bump the release to fix upgrade path

* Fri Sep 15 2023 Tomas Popela <tpopela@redhat.com> - 1.0.0-5.el8_8.2
- Added fix for mzbz#1819244

* Fri Sep 15 2023 Martin Stransky <stransky@redhat.com> - 1.0.0-5.el8_8.1
- Added fix for CVE-2023-4863

* Thu May 27 2021 Martin Stransky <stransky@redhat.com> - 1.0.0-5
- Added fixes for rhbz#1956853, rhbz#1956856, rhbz#1956868, rhbz#1956917

* Mon May 17 2021 Martin Stransky <stransky@redhat.com> - 1.0.0-3
- Added fixes for rhbz#1956829, rhbz#1956843, rhbz#1956919

* Thu Apr 26 2018 Sandro Mani <manisandro@gmail.com> - 1.0.0-1
- Update to 1.0.0

* Tue Feb 27 2018 Sandro Mani <manisandro@gmail.com> - 0.6.1-8
- Fix LDFLAGS not passed when building libwebp_jni.so (#1548718)

* Mon Feb 26 2018 Sandro Mani <manisandro@gmail.com> - 0.6.1-7
- More big-endian fixes

* Fri Feb 16 2018 Sandro Mani <manisandro@gmail.com> - 0.6.1-6
- Backport another big-endian fix

* Fri Feb 16 2018 Sandro Mani <manisandro@gmail.com> - 0.6.1-5
- Backport upstream big-endian fix

* Tue Feb 13 2018 Sandro Mani <manisandro@gmail.com> - 0.6.1-4
- Rebuild (giflib)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Feb 03 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.1-2
- Switch to %%ldconfig_scriptlets

* Thu Nov 30 2017 Sandro Mani <manisandro@gmail.com> - 0.6.1-1
- Update to 0.6.1

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 01 2017 Sandro Mani <manisandro@gmail.com> - 0.6.0-1
- Update to 0.6.0

* Thu Dec 22 2016 Sandro Mani <manisandro@gmail.com> - 0.5.2-1
- Update to 0.5.2

* Sat Oct 29 2016 Sandro Mani <manisandro@gmail.com> - 0.5.1-2
- Backport e2affacc35f1df6cc3b1a9fa0ceff5ce2d0cce83 (CVE-2016-9085, rhbz#1389338)

* Fri Aug 12 2016 Sandro Mani <manisandro@gmail.com> - 0.5.1-1
- upstream release 0.5.1

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 28 2015 Sandro Mani <manisandro@gmail.com> - 0.5.0-1
- upstream release 0.5.0

* Fri Oct 30 2015 Sandro Mani <manisandro@gmail.com> - 0.4.4-1
- upstream release 0.4.4

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Mar 27 2015 Sandro Mani <manisandro@gmail.com> - 0.4.3-2
- Add BuildRequires: freeglut-devel to build vwebp

* Thu Mar 12 2015 Sandro Mani <manisandro@gmail.com> - 0.4.3-1
- upstream release 0.4.3

* Fri Oct 17 2014 Sandro Mani <manisandro@gmail.com> - 0.4.2-1
- upstream release 0.4.2

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Aug 13 2014 Peter Robinson <pbrobinson@fedoraproject.org> 0.4.1-2
- Use frename-registers cflag to fix FTBFS on aarch64

* Tue Aug 05 2014 Sandro Mani <manisandro@gmail.com> - 0.4.1-1
- upstream release 0.4.1

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Apr 08 2014 Jaromir Capik <jcapik@redhat.com> - 0.4.0-3
- Fixing endian checks (#962091)
- Fixing FTPBS caused by rpath presence

* Fri Mar 28 2014 Michael Simacek <msimacek@redhat.com> - 0.4.0-2
- Use Requires: java-headless rebuild (#1067528)

* Thu Jan 02 2014 Sandro Mani <manisandro@gmail.com> - 0.4.0-1
- upstream release 0.4.0

* Wed Oct 02 2013 Sandro Mani <manisandro@gmail.com> - 0.3.1-2
- enable webpdemux

* Sun Aug 04 2013 Sandro Mani <manisandro@gmail.com> - 0.3.1-1
- upstream release 0.3.1

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon May 13 2013 Rahul Sundaram <sundaram@fedoraproject.org> - 0.3.0-1
- upstream release 0.3.0
- enable gif2webp
- add build requires on giflib-devel and libtiff-devel
- use make_install and hardened macros
- list binaries explicitly

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jan 18 2013 Adam Tkac <atkac redhat com> - 0.2.1-2
- rebuild due to "jpeg8-ABI" feature drop

* Thu Dec 27 2012 Rahul Sundaram <sundaram@fedoraproject.org> - 0.2.1-1
- new upstream release 0.2.1

* Fri Dec 21 2012 Adam Tkac <atkac redhat com> - 0.1.3-3
- rebuild against new libjpeg

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Feb 02 2012 Rahul Sundaram <sundaram@fedoraproject.org> - 0.1.3-1
- Several spec improvements by Scott Tsai <scottt.tw@gmail.com>

* Wed May 25 2011 Rahul Sundaram <sundaram@fedoraproject.org> - 0.1.2-1
- Initial spec. Based on openSUSE one

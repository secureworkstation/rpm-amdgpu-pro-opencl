# This package is inspired and partially based on the AUR package
# by Christopher Snowhill, ipha, johnnybash and grmat.
# https://aur.archlinux.org/packages/opencl-amd/

# Download the source pkg with this command:
# wget --referer https://support.amd.com/en-us/kb-articles/Pages/AMDGPU-PRO-Driver-for-Linux-Release-Notes.aspx https://drivers.amd.com/drivers/linux/19.50/amdgpu-pro-19.50-967956-ubuntu-18.04.tar.xz

# This package creates a wrapper file "amdgporun" which is similar to "optirun"
# or "primusrun" from Bumblebee times. In short, it enables the proprietary
# amdgpu-pro OpenCL stack on demand. If you want to eg. run Blender with it, you
# launch it the following way:
#
# $ amdgporun blender

# Important:
# The AMDGPU-PRO EULA forbids you from redistributing the source package.
# Therefore it's illegal to distribute the .src.rpm or .rpm files to third
# parties.

%global major 19.50
%global minor 967956
%global distro ubuntu-18.04

# Version of downstream libdrm-amdgpu package
%global amdver 2.4.99

# RPM flags
%global debug_package %{nil}

Name:           amdgpu-pro-opencl
Version:        %{major}.%{minor}
Release:        1%{?dist}
Summary:        OpenCL ICD driver for AMD graphic cards

License:        EULA NON-REDISTRIBUTABLE
URL:            https://www.amd.com/en/support/kb/release-notes/rn-rad-lin-19-50-unified
Source0:        https://drivers.amd.com/drivers/linux/%{major}/amdgpu-pro-%{major}-%{minor}-%{distro}.tar.xz

ExclusiveArch:  x86_64
#BuildRequires:  
Requires:       ocl-icd
Requires:	libdrm

%description
OpenCL userspace driver as provided in the amdgpu-pro driver stack. This package
is intended to work along with the free amdgpu stack.


%prep
%setup -q -n amdgpu-pro-%{major}-%{minor}-%{distro}
mkdir files
ar x opencl-amdgpu-pro-icd_%{major}-%{minor}_amd64.deb
tar -xJC files -f data.tar.xz
ar x opencl-amdgpu-pro-comgr_%{major}-%{minor}_amd64.deb
tar -xJC files -f data.tar.xz
# This one is probably unneeded for most users, but you never know.
ar x opencl-amdgpu-pro-dev_%{major}-%{minor}_amd64.deb
tar -xJC files -f data.tar.xz
ar x opencl-orca-amdgpu-pro-icd_%{major}-%{minor}_amd64.deb
tar -xJC files -f data.tar.xz
# I'm not sure if it needs appprofiles, but strace shows that /etc/amd/amdapfxx.blb is referenced.
ar x libgl1-amdgpu-pro-appprofiles_%{major}-%{minor}_all.deb
tar -xJC files -f data.tar.xz
ar x libdrm-amdgpu-amdgpu1_%{amdver}-%{minor}_amd64.deb
tar -xJC files -f data.tar.xz

%build
echo '#!/bin/bash' > amdgporun
echo 'export LD_LIBRARY_PATH=/usr/lib64/amdgpu-pro-opencl' >> amdgporun
echo 'exec "$@"' >> amdgporun

pushd files/opt/amdgpu-pro/lib/x86_64-linux-gnu/
sed -i "s|libdrm_amdgpu|libdrm_amdgpo|g" libamdocl-orca64.so libamdocl64.so
sed -i "s|/opt/amdgpu-pro/lib/x86_64-linux-gnu/|/usr/lib64/amdgpu-pro-opencl/////////|g" libamdocl-orca64.so
sed -i "s|/opt/amdgpu-pro/lib/i386-linux-gnu/|/usr/lib/amdgpu-pro-opencl/////////|g" libamdocl-orca64.so
popd

pushd files/opt/amdgpu/lib/x86_64-linux-gnu/
sed -i "s|/opt/amdgpu/share/|/usr/share////////|g" libdrm_amdgpu.so.1.0.0
mv libdrm_{amdgpu,amdgpo}.so.1.0.0
rm libdrm_amdgpu.so.1
popd

%install
mkdir -p %{buildroot}%{_libdir}/amdgpu-pro-opencl/
mkdir -p %{buildroot}%{_sysconfdir}/amd/
mkdir -p %{buildroot}%{_sysconfdir}/OpenCL/vendors/
mkdir -p %{buildroot}%{_docdir}/amdgpu-pro-opencl/
mkdir -p %{buildroot}%{_bindir}/

install -p -m755 files/opt/amdgpu-pro/lib/x86_64-linux-gnu/* %{buildroot}%{_libdir}/amdgpu-pro-opencl/
install -p -m755 files/opt/amdgpu/lib/x86_64-linux-gnu/* %{buildroot}%{_libdir}/amdgpu-pro-opencl/
install -p -m644 files/etc/amd/amdapfxx.blb %{buildroot}%{_sysconfdir}/amd/
install -p -m644 files/etc/OpenCL/vendors/* %{buildroot}%{_sysconfdir}/OpenCL/vendors/
install -p -m644 files/usr/share/doc/opencl-amdgpu-pro-icd/copyright %{buildroot}%{_docdir}/amdgpu-pro-opencl/COPYRIGHT-AMDGPU-PRO
install -p -m644 files/usr/share/doc/libdrm-amdgpu-amdgpu1/copyright %{buildroot}%{_docdir}/amdgpu-pro-opencl/COPYRIGHT-AMDGPU
install -p -m755 amdgporun %{buildroot}%{_bindir}/

ln -s libdrm_amdgpo.so.1.0.0 %{buildroot}%{_libdir}/amdgpu-pro-opencl/libdrm_amdgpo.so.1

%files
%license %{_docdir}/amdgpu-pro-opencl/COPYRIGHT-AMDGPU-PRO
%license %{_docdir}/amdgpu-pro-opencl/COPYRIGHT-AMDGPU
%{_libdir}/amdgpu-pro-opencl/
%{_sysconfdir}/OpenCL/vendors/*
%{_sysconfdir}/amd/
%{_bindir}/amdgporun


%changelog
* Tue Mar 10 2020 secureworkstation - 19.50.967956-1
- Initial release

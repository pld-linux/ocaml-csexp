#
# Conditional build:
%bcond_without	ocaml_opt	# skip building native optimized binaries (bytecode is always built)
%bcond_with	dune		# build with dune, this is off due to circular deps

# not yet available on x32 (ocaml 4.02.1), update when upstream will support it
%ifnarch %{ix86} %{x8664} %{arm} aarch64 ppc sparc sparcv9
%undefine	with_ocaml_opt
%endif

%if %{without ocaml_opt}
%define		_enable_debug_packages	0
%endif

%define		module	csexp
Summary:	Parsing and printing of S-expressions in canonical form
Name:		ocaml-%{module}
Version:	1.4.0
Release:	1
License:	MIT
Source0:	https://github.com/ocaml-dune/csexp/releases/download/%{version}/%{module}-%{version}.tbz
# Source0-md5:	d6b5866be24bf8730c127eedca4dc447
URL:		https://github.com/ocaml-dune/csexp
# Depend on Stdlib.Result instead of ocaml-result.
Patch0:		%{name}-result.patch
BuildRequires:	ocaml >= 4.02.3
%if %{with dune}
BuildRequires:	ocaml-dune >= 1.11
BuildRequires:	ocaml-odoc
BuildRequires:	ocaml-result-devel >= 1.5
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This project provides minimal support for parsing and printing
S-expressions in canonical form, which is a very simple and canonical
binary encoding of S-expressions.

%package devel
Summary:	Development files for %{name}
Requires:	%{name} = %{version}-%{release}
%if %{with dune}
Requires:	ocaml-result-devel
%endif

%description devel
The %{name}-devel package contains libraries and signature files for
developing applications that use %{name}.

%prep
%setup -q -n %{module}-%{version}
%if %{without dune}
%patch0 -p1
%endif

%build
%if %{with dune}
dune build %{?_smp_mflags} --display=verbose @install
dune build %{?_smp_mflags} @doc
%else
OFLAGS="-strict-sequence -strict-formats -short-paths -keep-locs -g -opaque"
OCFLAGS="$OFLAGS -bin-annot"
cd src
ocamlc $OCFLAGS -output-obj csexp.mli
ocamlc $OCFLAGS -a -o csexp.cma csexp.ml
%if %{with ocaml_opt}
ocamlopt $OFLAGS -ccopt "%{rpmcflags}" -cclib "%{rpmldflags}" -a \
	-o csexp.cmxa csexp.ml
ocamlopt $OFLAGS -ccopt "%{rpmcflags}" -cclib "%{rpmldflags}" -shared \
	-o csexp.cmxs csexp.ml
%endif
%endif

%install
rm -rf $RPM_BUILD_ROOT
%if %{with dune}
dune install --destdir=$RPM_BUILD_ROOT

# We do not want the dune markers
find _build/default/_doc/_html -name .dune-keep -delete

# We do not want the ml files
find $RPM_BUILD_ROOT%{_libdir}/ocaml -name \*.ml -delete

# We install the documentation with the doc macro
rm -fr $RPM_BUILD_ROOT%{_prefix}/doc
%else
# Install without dune.  See comment at the top.
install -d $RPM_BUILD_ROOT%{_libdir}/ocaml/%{module}
cp -p src/csexp.{cma,cmi,cmt,cmti,mli} $RPM_BUILD_ROOT%{_libdir}/ocaml/%{module}
%if %{with ocaml_opt}
cp -p src/csexp.{a,cmx,cmxa,cmxs} $RPM_BUILD_ROOT%{_libdir}/ocaml/%{module}
%endif

cp -p csexp.opam $RPM_BUILD_ROOT%{_libdir}/ocaml/%{module}/opam

cat >> $RPM_BUILD_ROOT%{_libdir}/ocaml/%{module}/META << EOF
version = "%{version}"
description = "Parsing and printing of S-expressions in canonical form"
archive(byte) = "csexp.cma"
%ifarch %{ocaml_native_compiler}
archive(native) = "csexp.cmxa"
%endif
plugin(byte) = "csexp.cma"
%ifarch %{ocaml_native_compiler}
plugin(native) = "csexp.cmxs"
%endif
EOF

cat >> $RPM_BUILD_ROOT%{_libdir}/ocaml/%{module}/dune-package << EOF
(lang dune 2.8)
(name csexp)
(version %{version})
(library
 (name csexp)
 (kind normal)
%if %{with ocaml_opt}
 (archives (byte csexp.cma) (native csexp.cmxa))
 (plugins (byte csexp.cma) (native csexp.cmxs))
 (native_archives csexp.a)
%else
 (archives (byte csexp.cma))
 (plugins (byte csexp.cma))
%endif
 (main_module_name Csexp)
%if %{with ocaml_opt}
 (modes byte native)
%else
 (modes byte)
%endif
 (modules
  (singleton (name Csexp) (obj_name csexp) (visibility public) (impl) (intf))))
EOF
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md
%doc LICENSE.md
%dir %{_libdir}/ocaml/%{module}/
%{_libdir}/ocaml/%{module}/META
%{_libdir}/ocaml/%{module}/*.cma
%{_libdir}/ocaml/%{module}/*.cmi
%if %{with ocaml_opt}
%{_libdir}/ocaml/%{module}/*.cmxs
%endif

%files devel
%defattr(644,root,root,755)
%{_libdir}/ocaml/%{module}/dune-package
%{_libdir}/ocaml/%{module}/opam
%if %{with ocaml_opt}
%{_libdir}/ocaml/%{module}/*.a
%{_libdir}/ocaml/%{module}/*.cmx
%{_libdir}/ocaml/%{module}/*.cmxa
%endif
%{_libdir}/ocaml/%{module}/*.cmt
%{_libdir}/ocaml/%{module}/*.cmti
%{_libdir}/ocaml/%{module}/*.mli

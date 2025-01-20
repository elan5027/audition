#!/bin/bash
set -e

# Install required tools
dnf install -y rpmdevtools

# Create working directory
cd /tmp

# Download required packages
dnf download cairo gdk-pixbuf2 libffi pango expat libmount libuuid libblkid glib2 libthai fribidi harfbuzz libdatrie freetype graphite2 libbrotli libpng fontconfig shared-mime-info

# Extract RPM files
rpmdev-extract -- *rpm

# Create target directory
mkdir -p /opt/lib

# Copy necessary libraries
cp -P -r /tmp/*/usr/lib64/* /opt/lib
for f in $(find /tmp  -type f  -name 'lib*.so*'); do 
  cp "$f" /opt/lib/$(python3 -c "import re; print(re.match(r'^(.*.so.\\d+).*$', '$(basename $f)').groups()[0])")
done

# Generate loaders cache for gdk-pixbuf
PIXBUF_BIN=$(find /tmp -name gdk-pixbuf-query-loaders-64)
GDK_PIXBUF_MODULEDIR=$(find /opt/lib/gdk-pixbuf-2.0/ -name loaders)
export GDK_PIXBUF_MODULEDIR
$PIXBUF_BIN > /opt/lib/loaders.cache

# Install Python dependencies
RUNTIME=$(grep AWS_EXECUTION_ENV "$LAMBDA_RUNTIME_DIR/bootstrap" | cut -d _ -f 5)
mkdir -p "/opt/python/lib/$RUNTIME/site-packages"
python3 -m pip install "weasyprint" -t "/opt/python/lib/$RUNTIME/site-packages"

# Create ZIP archive
cd /opt
zip -r9 /out/layer.zip lib/* python/*

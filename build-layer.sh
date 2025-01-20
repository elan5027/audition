#!/bin/bash
set -e

# Install required tools
yum install -y rpmdevtools python3 python3-pip zip yum-utils

# Create working directory
cd /tmp

# Download only required packages using yumdownloader
yumdownloader --resolve cairo gtk3 gdk-pixbuf2 libffi pango expat \
  glib2 shared-mime-info fontconfig libpng freetype

# Extract RPM files
rpmdev-extract -- *.rpm

# Create target directory
mkdir -p /opt/lib

# Copy only necessary libraries
find /tmp -type f -name 'lib*.so*' -exec cp -P {} /opt/lib/ \;

# Generate loaders cache for gdk-pixbuf
PIXBUF_BIN=$(find /tmp -name gdk-pixbuf-query-loaders-64 | head -n 1)
if [[ -z "$PIXBUF_BIN" ]]; then
  echo "Error: gdk-pixbuf-query-loaders-64 not found."
  exit 1
fi

GDK_PIXBUF_MODULEDIR=$(find /opt/lib/gdk-pixbuf-2.0/ -name loaders | head -n 1)
if [[ -z "$GDK_PIXBUF_MODULEDIR" ]]; then
  echo "Error: GDK_PIXBUF_MODULEDIR not found."
  exit 1
fi

export GDK_PIXBUF_MODULEDIR
$PIXBUF_BIN > /opt/lib/loaders.cache

# Install Python dependencies and strip unneeded files
RUNTIME=$(grep AWS_EXECUTION_ENV "$LAMBDA_RUNTIME_DIR/bootstrap" | cut -d _ -f 5)
PYTHON_LIB="/opt/python/lib/$RUNTIME/site-packages"
mkdir -p "$PYTHON_LIB"
python3 -m pip install "weasyprint" --no-cache-dir -t "$PYTHON_LIB"

# Remove unneeded files to reduce size
find "$PYTHON_LIB" -name "*.pyc" -delete
find "$PYTHON_LIB" -type d -name "__pycache__" -exec rm -rf {} +
strip --strip-unneeded /opt/lib/* || echo "No files to strip."

# Create ZIP archive
cd /opt
zip -r9 /out/layer.zip lib/* python/*


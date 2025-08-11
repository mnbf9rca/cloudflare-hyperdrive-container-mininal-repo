#!/bin/bash
# Deploy script for Hyperdrive DNS test

set -e

echo "=== Hyperdrive DNS Issue - Deployment Script ==="
echo ""

# Check prerequisites
if ! command -v wrangler &> /dev/null; then
    echo "Error: wrangler CLI not found"
    echo "Install with: npm install -g wrangler"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "Error: Docker not found"
    echo "Please install Docker to build containers"
    exit 1
fi

# Check if logged in to Cloudflare
if ! wrangler whoami &> /dev/null; then
    echo "Error: Not logged in to Cloudflare"
    echo "Run: wrangler login"
    exit 1
fi

# Get Hyperdrive ID from wrangler.toml
HYPERDRIVE_ID=$(grep -A1 '\[\[hyperdrive\]\]' wrangler.toml | grep 'id' | cut -d'"' -f2)

if [ "$HYPERDRIVE_ID" = "66c4c2b923f89002cbc61b8192b83e63" ]; then
    echo "WARNING: Using default Hyperdrive ID from example"
    echo "Please update wrangler.toml with your actual Hyperdrive ID"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Using Hyperdrive ID: $HYPERDRIVE_ID"
echo ""

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Deploy
echo "Deploying to Cloudflare Workers..."
wrangler deploy

echo ""
echo "=== Deployment Complete ==="
echo ""


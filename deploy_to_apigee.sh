#!/usr/bin/env bash
#
# Advent of Agents - Day 20: Deploy Apigee MCP Proxy
#
# Deploys the advent-day20-mcp-proxy starter bundle to your Apigee organization
# using Apigee Management APIs.
#

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo '')}"
ENV_NAME="${ENV_NAME:-eval}"
PROXY_NAME="advent-day20-mcp-proxy"
BUNDLE_ZIP="advent-day20-mcp-proxy.zip"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "Error: PROJECT_ID is not set."
  echo "Usage:"
  echo "  export PROJECT_ID='<your-google-cloud-project-id>'"
  echo "  export ENV_NAME='<your-apigee-environment>'  # Defaults to 'eval'"
  echo "  ./deploy_to_apigee.sh"
  exit 1
fi

echo "=========================================================="
echo "Advent of Agents Day 20: Deploying Apigee MCP Proxy"
echo "Project:     ${PROJECT_ID}"
echo "Environment: ${ENV_NAME}"
echo "Proxy Name:  ${PROXY_NAME}"
echo "Bundle:      ${BUNDLE_ZIP}"
echo "=========================================================="

if [[ ! -f "${BUNDLE_ZIP}" ]]; then
  echo "Error: ${BUNDLE_ZIP} not found in current directory."
  exit 1
fi

TOKEN=$(gcloud auth print-access-token)

echo "1. Uploading proxy bundle revision..."
UPLOAD_RESP=$(curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@${BUNDLE_ZIP}" \
  "https://apigee.googleapis.com/v1/organizations/${PROJECT_ID}/apis?action=import&name=${PROXY_NAME}")

REVISION=$(echo "${UPLOAD_RESP}" | grep -o '"revision": "[^"]*"' | head -n1 | cut -d'"' -f4 || echo "1")
echo "-> Imported revision: ${REVISION}"

echo "2. Deploying revision ${REVISION} to environment '${ENV_NAME}'..."
DEPLOY_RESP=$(curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  "https://apigee.googleapis.com/v1/organizations/${PROJECT_ID}/environments/${ENV_NAME}/apis/${PROXY_NAME}/revisions/${REVISION}/deployments?override=true")

echo "-> Deployment response:"
echo "${DEPLOY_RESP}"

echo "=========================================================="
echo "Apigee MCP Proxy deployed successfully!"
echo "BasePath: /v1/mcp"
echo "Test using: python3 demo_runner.py"
echo "=========================================================="

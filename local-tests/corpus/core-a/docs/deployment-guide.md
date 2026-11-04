# Deployment guide — customer portal (synthetic)

## Prerequisites
REQUIRES: app/main.py
REQUIRES: config/prod-config.yaml

The production configuration `config/prod-config.yaml` holds the live
database endpoints. It is intentionally NOT stored in this folder; the
operator must supply it before redeploying.

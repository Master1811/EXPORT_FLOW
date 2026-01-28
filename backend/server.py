# Entry point for uvicorn - imports from modular app structure
from app.main import app

# This file serves as the entry point for the backend server
# All application logic is now organized in the /app directory:
#
# app/
#   ├── main.py              # FastAPI app factory and root endpoints
#   ├── core/
#   │   ├── config.py        # Settings and configuration
#   │   ├── database.py      # MongoDB connection
#   │   ├── security.py      # JWT and password utilities
#   │   └── dependencies.py  # FastAPI dependencies (auth)
#   ├── auth/                # Authentication module
#   ├── companies/           # Company management
#   ├── shipments/           # Shipment CRUD
#   ├── documents/           # Trade documents
#   ├── payments/            # Payments & receivables
#   ├── forex/               # Foreign exchange rates
#   ├── gst/                 # GST compliance
#   ├── incentives/          # RoDTEP/RoSCTL
#   ├── ai/                  # AI assistant
#   ├── connectors/          # Bank/GST/Customs connectors
#   ├── credit/              # Credit intelligence
#   ├── jobs/                # Async job tracking
#   ├── notifications/       # Notification system
#   └── common/              # Shared utilities

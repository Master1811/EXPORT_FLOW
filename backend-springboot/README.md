# Export Flow – Java Spring Boot Backend

Drop-in replacement for the Python FastAPI backend. Same API contract and behavior so the existing frontend works without changes.

## Requirements

- Java 17+
- Maven 3.6+
- MongoDB (same as Python backend)

## Configuration

Environment variables (same as Python):

| Variable           | Default              | Description        |
|--------------------|----------------------|--------------------|
| `MONGO_URL`        | `mongodb://localhost:27017` | MongoDB connection |
| `DB_NAME`          | `test_database`     | MongoDB database   |
| `JWT_SECRET_KEY`   | `default-secret-key`| JWT signing key    |
| `JWT_EXPIRE_MINUTES` | `1440`            | Token expiry (min) |
| `CORS_ORIGINS`     | `*`                 | Allowed CORS origins (comma-separated) |
| `EMERGENT_LLM_KEY` | (empty)             | Optional AI/LLM key |

## Build & run

```bash
mvn clean package
java -jar target/export-flow-backend-1.0.0.jar
```

Or with Maven:

```bash
mvn spring-boot:run
```

Server runs on port **8080** by default. Base URL for the API is **http://localhost:8080/api** (context path is `/api`).

Frontend: set `REACT_APP_BACKEND_URL=http://localhost:8080` so the app calls `http://localhost:8080/api`.

## API

All routes and request/response shapes match the Python backend:

- **Auth**: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`, `/api/auth/refresh`
- **Company**: `/api/company`, `/api/company/{id}`
- **Shipments**: `/api/shipments`, `/api/shipments/{id}`
- **Documents**: `/api/shipments/{id}/invoice`, packing-list, shipping-bill, documents list; OCR and bulk upload
- **Payments**: `/api/payments`, receivables, aging
- **Forex**: `/api/forex/rate`, `/api/forex/latest`, `/api/forex/history/{currency}`
- **GST**: input credit, summary, refund, LUT
- **Incentives**: RoDTEP eligibility, calculate, lost-money, summary
- **AI**: query, refund/cashflow forecast, incentive optimizer, risk alerts
- **Connectors**: bank, GST, customs connect/sync
- **Credit**: buyer score, company score, payment behavior
- **Jobs**: `/api/jobs/{id}/status`
- **Notifications**: send, history
- **Dashboard**: stats, charts
- **Files**: upload, get, delete
- **Webhooks**: WhatsApp, bank
- **Root**: `/api/`, `/api/health`, `/api/metrics`, `/api/audit/logs`

## Project layout

- `config/` – App config, security, CORS
- `security/` – JWT filter, `CurrentUser`, `JwtUtil`
- `dto/` – Request/response DTOs (snake_case JSON via `@JsonProperty`)
- `entity/` – MongoDB documents (`@Field` for snake_case where needed)
- `repository/` – Spring Data MongoDB repositories
- `service/` – Business logic
- `controller/` – REST controllers
- `exception/` – Global exception handler
- `util/` – ID and date helpers

## AI /query

The Python backend used Emergent LLM for `/api/ai/query`. The Java version returns the same response structure but with a placeholder message. To use a real LLM, implement the call in `AIService.query()` (e.g. HTTP client to your LLM API or an Emergent/Java SDK if available).

# Migration Architecture Guide: FastAPI/MongoDB → Spring Boot/PostgreSQL

## Executive Summary

This document provides a comprehensive roadmap for migrating the **ExportFlow** platform from the current **FastAPI + MongoDB** stack to **Spring Boot + PostgreSQL**. The migration preserves all business logic while leveraging Java's enterprise ecosystem for better scalability, type safety, and integration with corporate IT infrastructure.

---

## Table of Contents

1. [Current Architecture Overview](#current-architecture-overview)
2. [Target Architecture](#target-architecture)
3. [Database Migration Strategy](#database-migration-strategy)
4. [API Migration Map](#api-migration-map)
5. [Code Structure Mapping](#code-structure-mapping)
6. [Authentication Migration](#authentication-migration)
7. [Data Migration Scripts](#data-migration-scripts)
8. [Deployment Architecture](#deployment-architecture)
9. [Testing Strategy](#testing-strategy)
10. [Rollback Plan](#rollback-plan)

---

## 1. Current Architecture Overview

### Technology Stack
```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│   React 18 + TailwindCSS + Shadcn UI + Recharts             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
│   FastAPI (Python 3.11) + Pydantic + Motor (async MongoDB)  │
│   JWT Authentication + BCrypt Password Hashing               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        DATABASE                              │
│   MongoDB (Document Store) + GridFS (File Storage)           │
└─────────────────────────────────────────────────────────────┘
```

### Current Module Structure
```
/app/backend/app/
├── auth/           # JWT authentication
├── shipments/      # Shipment CRUD + e-BRC monitoring
├── payments/       # Payments + Aging dashboard
├── incentives/     # RoDTEP/RoSCTL calculator
├── documents/      # Trade document management
├── gst/            # GST compliance
├── forex/          # Currency rates
├── ai/             # AI assistant (Gemini)
├── credit/         # Buyer credit intelligence
├── connectors/     # External integrations
├── exports/        # Async export service
└── core/           # Config, DB, Dependencies
```

---

## 2. Target Architecture

### Spring Boot Stack
```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│   Next.js 14 (App Router) + TailwindCSS + Shadcn UI         │
│   (Optional: Keep React if preferred)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
│   Spring Boot 3.2 + Spring Security + JPA/Hibernate         │
│   Java 21 (LTS) + Lombok + MapStruct                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        DATABASE                              │
│   PostgreSQL 16 + Row-Level Security (RLS)                  │
│   + pgvector (for AI embeddings) + S3 (file storage)        │
└─────────────────────────────────────────────────────────────┘
```

### Target Module Structure (Spring Boot)
```
src/main/java/com/exportflow/
├── config/
│   ├── SecurityConfig.java
│   ├── JwtConfig.java
│   └── CorsConfig.java
├── auth/
│   ├── controller/AuthController.java
│   ├── service/AuthService.java
│   ├── dto/LoginRequest.java
│   ├── entity/User.java
│   └── repository/UserRepository.java
├── shipment/
│   ├── controller/ShipmentController.java
│   ├── service/ShipmentService.java
│   ├── dto/ShipmentDTO.java
│   ├── entity/Shipment.java
│   └── repository/ShipmentRepository.java
├── payment/
├── incentive/
├── document/
├── gst/
├── forex/
├── ai/
├── credit/
├── connector/
└── export/
```

---

## 3. Database Migration Strategy

### Schema Design (PostgreSQL)

```sql
-- Users table with RLS
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    company_id UUID REFERENCES companies(id),
    role VARCHAR(50) DEFAULT 'user',
    token_version TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Companies table
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    gstin VARCHAR(15),
    pan VARCHAR(10),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shipments table
CREATE TABLE shipments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_number VARCHAR(50) UNIQUE NOT NULL,
    company_id UUID REFERENCES companies(id) NOT NULL,
    buyer_name VARCHAR(255) NOT NULL,
    buyer_country VARCHAR(100) NOT NULL,
    buyer_email VARCHAR(255),
    buyer_phone VARCHAR(50),
    buyer_pan VARCHAR(10),
    buyer_bank_account VARCHAR(50),
    destination_port VARCHAR(100),
    origin_port VARCHAR(100),
    incoterm VARCHAR(10) DEFAULT 'FOB',
    currency VARCHAR(3) DEFAULT 'USD',
    total_value DECIMAL(15, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    expected_ship_date DATE,
    actual_ship_date DATE,
    product_description TEXT,
    hs_codes TEXT[], -- PostgreSQL array
    ebrc_status VARCHAR(50) DEFAULT 'pending',
    ebrc_filed_date DATE,
    ebrc_number VARCHAR(50),
    ebrc_due_date DATE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Row-Level Security for multi-tenancy
ALTER TABLE shipments ENABLE ROW LEVEL SECURITY;

CREATE POLICY shipment_company_isolation ON shipments
    FOR ALL
    USING (company_id = current_setting('app.company_id')::UUID);

-- Payments table
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id UUID REFERENCES shipments(id) NOT NULL,
    company_id UUID REFERENCES companies(id) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_date DATE,
    payment_mode VARCHAR(50),
    bank_reference VARCHAR(100),
    exchange_rate DECIMAL(10, 4),
    inr_amount DECIMAL(15, 2),
    status VARCHAR(50) DEFAULT 'received',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Token blacklist for JWT invalidation
CREATE TABLE token_blacklist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash VARCHAR(64) NOT NULL, -- Store hash, not full token
    reason VARCHAR(50),
    blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_token_blacklist_hash ON token_blacklist(token_hash);

-- Export jobs
CREATE TABLE export_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) NOT NULL,
    user_id UUID REFERENCES users(id) NOT NULL,
    export_type VARCHAR(50) NOT NULL,
    format VARCHAR(10) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    total_rows INTEGER DEFAULT 0,
    file_path VARCHAR(500),
    file_name VARCHAR(255),
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Incentives (calculated values)
CREATE TABLE incentives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id UUID REFERENCES shipments(id) NOT NULL,
    company_id UUID REFERENCES companies(id) NOT NULL,
    hs_code VARCHAR(20),
    fob_value DECIMAL(15, 2),
    rodtep_rate DECIMAL(5, 2),
    rosctl_rate DECIMAL(5, 2),
    drawback_rate DECIMAL(5, 2),
    total_incentive DECIMAL(15, 2),
    status VARCHAR(50) DEFAULT 'calculated',
    claimed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_shipments_company ON shipments(company_id);
CREATE INDEX idx_shipments_status ON shipments(status);
CREATE INDEX idx_payments_shipment ON payments(shipment_id);
CREATE INDEX idx_incentives_shipment ON incentives(shipment_id);
```

### MongoDB to PostgreSQL Type Mapping

| MongoDB Type | PostgreSQL Type | Notes |
|--------------|-----------------|-------|
| ObjectId | UUID | Use gen_random_uuid() |
| String | VARCHAR / TEXT | Use TEXT for long content |
| Number (int) | INTEGER / BIGINT | |
| Number (float) | DECIMAL(15,2) | For money values |
| Boolean | BOOLEAN | |
| Date | TIMESTAMP | Store in UTC |
| Array | TEXT[] / JSONB | Arrays for simple types, JSONB for complex |
| Object | JSONB | For flexible schema fields |

---

## 4. API Migration Map

### Endpoint Mapping: FastAPI → Spring Boot

| FastAPI Endpoint | Spring Boot Endpoint | Controller Method |
|-----------------|---------------------|-------------------|
| `POST /api/auth/register` | `POST /api/auth/register` | `AuthController.register()` |
| `POST /api/auth/login` | `POST /api/auth/login` | `AuthController.login()` |
| `POST /api/auth/logout` | `POST /api/auth/logout` | `AuthController.logout()` |
| `POST /api/auth/change-password` | `POST /api/auth/change-password` | `AuthController.changePassword()` |
| `GET /api/shipments` | `GET /api/shipments` | `ShipmentController.getAll()` |
| `POST /api/shipments` | `POST /api/shipments` | `ShipmentController.create()` |
| `GET /api/shipments/{id}` | `GET /api/shipments/{id}` | `ShipmentController.getById()` |
| `PUT /api/shipments/{id}` | `PUT /api/shipments/{id}` | `ShipmentController.update()` |
| `DELETE /api/shipments/{id}` | `DELETE /api/shipments/{id}` | `ShipmentController.delete()` |
| `GET /api/shipments/ebrc-dashboard` | `GET /api/shipments/ebrc-dashboard` | `ShipmentController.getEbrcDashboard()` |
| `PUT /api/shipments/{id}/ebrc` | `PUT /api/shipments/{id}/ebrc` | `ShipmentController.updateEbrc()` |
| `GET /api/payments/receivables/aging-dashboard` | `GET /api/payments/receivables/aging-dashboard` | `PaymentController.getAgingDashboard()` |
| `POST /api/exports` | `POST /api/exports` | `ExportController.createExport()` |
| `GET /api/exports/download/{id}` | `GET /api/exports/download/{id}` | `ExportController.download()` |

### Spring Boot Controller Example

```java
@RestController
@RequestMapping("/api/shipments")
@RequiredArgsConstructor
public class ShipmentController {

    private final ShipmentService shipmentService;

    @GetMapping
    public ResponseEntity<List<ShipmentDTO>> getAllShipments(
            @RequestParam(required = false) String status,
            @AuthenticationPrincipal UserPrincipal user) {
        return ResponseEntity.ok(shipmentService.findAll(user.getCompanyId(), status));
    }

    @PostMapping
    public ResponseEntity<ShipmentDTO> createShipment(
            @Valid @RequestBody CreateShipmentRequest request,
            @AuthenticationPrincipal UserPrincipal user) {
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(shipmentService.create(request, user));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ShipmentDTO> getShipment(
            @PathVariable UUID id,
            @AuthenticationPrincipal UserPrincipal user) {
        return ResponseEntity.ok(shipmentService.findById(id, user.getCompanyId()));
    }

    @GetMapping("/ebrc-dashboard")
    public ResponseEntity<EbrcDashboardDTO> getEbrcDashboard(
            @AuthenticationPrincipal UserPrincipal user) {
        return ResponseEntity.ok(shipmentService.getEbrcDashboard(user.getCompanyId()));
    }
}
```

---

## 5. Code Structure Mapping

### Python → Java Equivalents

| Python/FastAPI | Java/Spring Boot |
|---------------|------------------|
| Pydantic `BaseModel` | Java Record / DTO with `@Valid` |
| `@router.get("/path")` | `@GetMapping("/path")` |
| `@router.post("/path")` | `@PostMapping("/path")` |
| `Depends(get_current_user)` | `@AuthenticationPrincipal` |
| `HTTPException` | Custom `@ControllerAdvice` |
| `async def service_method()` | `CompletableFuture<T>` or `@Async` |
| Motor (async MongoDB) | Spring Data JPA + Hibernate |
| Pydantic validators | Jakarta Bean Validation |

### Service Layer Example

```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class ShipmentService {

    private final ShipmentRepository shipmentRepository;
    private final ShipmentMapper shipmentMapper;
    private final PiiMaskingService piiMaskingService;

    public List<ShipmentDTO> findAll(UUID companyId, String status) {
        List<Shipment> shipments;
        if (status != null) {
            shipments = shipmentRepository.findByCompanyIdAndStatus(companyId, status);
        } else {
            shipments = shipmentRepository.findByCompanyId(companyId);
        }
        return shipments.stream()
            .map(s -> piiMaskingService.maskSensitiveFields(shipmentMapper.toDto(s)))
            .toList();
    }

    @Transactional
    public ShipmentDTO create(CreateShipmentRequest request, UserPrincipal user) {
        Shipment shipment = shipmentMapper.toEntity(request);
        shipment.setCompanyId(user.getCompanyId());
        shipment.setCreatedBy(user.getId());
        
        // Calculate e-BRC due date
        if (shipment.getActualShipDate() != null) {
            shipment.setEbrcDueDate(shipment.getActualShipDate().plusDays(60));
        }
        
        return shipmentMapper.toDto(shipmentRepository.save(shipment));
    }
}
```

---

## 6. Authentication Migration

### JWT Configuration (Spring Security)

```java
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtTokenProvider jwtTokenProvider;
    private final TokenBlacklistService tokenBlacklistService;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/login", "/api/auth/register").permitAll()
                .requestMatchers("/api/health").permitAll()
                .anyRequest().authenticated())
            .addFilterBefore(
                new JwtAuthenticationFilter(jwtTokenProvider, tokenBlacklistService),
                UsernamePasswordAuthenticationFilter.class)
            .build();
    }
}
```

### Token Blacklist Service

```java
@Service
@RequiredArgsConstructor
public class TokenBlacklistService {

    private final TokenBlacklistRepository repository;

    public void blacklistToken(String token, String reason) {
        String tokenHash = DigestUtils.sha256Hex(token);
        LocalDateTime expiresAt = extractExpiration(token);
        
        TokenBlacklist blacklist = new TokenBlacklist();
        blacklist.setTokenHash(tokenHash);
        blacklist.setReason(reason);
        blacklist.setExpiresAt(expiresAt);
        
        repository.save(blacklist);
    }

    public boolean isBlacklisted(String token) {
        String tokenHash = DigestUtils.sha256Hex(token);
        return repository.existsByTokenHash(tokenHash);
    }

    @Scheduled(cron = "0 0 * * * *") // Hourly cleanup
    public void cleanupExpiredTokens() {
        repository.deleteByExpiresAtBefore(LocalDateTime.now());
    }
}
```

---

## 7. Data Migration Scripts

### MongoDB → PostgreSQL Migration Script

```python
#!/usr/bin/env python3
"""
MongoDB to PostgreSQL Migration Script
Run: python migrate_to_postgres.py
"""

import asyncio
import uuid
from datetime import datetime
import motor.motor_asyncio
import asyncpg

MONGO_URL = "mongodb://localhost:27017"
MONGO_DB = "exportflow"
PG_URL = "postgresql://user:pass@localhost:5432/exportflow"

async def migrate():
    # Connect to MongoDB
    mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    mongo_db = mongo[MONGO_DB]
    
    # Connect to PostgreSQL
    pg = await asyncpg.connect(PG_URL)
    
    print("Starting migration...")
    
    # 1. Migrate companies
    print("Migrating companies...")
    companies = await mongo_db.companies.find({}, {"_id": 0}).to_list(10000)
    for c in companies:
        await pg.execute("""
            INSERT INTO companies (id, name, created_at)
            VALUES ($1, $2, $3)
            ON CONFLICT (id) DO NOTHING
        """, uuid.UUID(c["id"]), c["name"], 
            datetime.fromisoformat(c["created_at"].replace("Z", "+00:00")))
    print(f"  Migrated {len(companies)} companies")
    
    # 2. Migrate users
    print("Migrating users...")
    users = await mongo_db.users.find({}, {"_id": 0}).to_list(10000)
    for u in users:
        await pg.execute("""
            INSERT INTO users (id, email, password_hash, full_name, company_id, role, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO NOTHING
        """, uuid.UUID(u["id"]), u["email"], u["password"], u["full_name"],
            uuid.UUID(u["company_id"]) if u.get("company_id") else None,
            u.get("role", "user"),
            datetime.fromisoformat(u["created_at"].replace("Z", "+00:00")))
    print(f"  Migrated {len(users)} users")
    
    # 3. Migrate shipments
    print("Migrating shipments...")
    shipments = await mongo_db.shipments.find({}, {"_id": 0}).to_list(100000)
    for s in shipments:
        await pg.execute("""
            INSERT INTO shipments (
                id, shipment_number, company_id, buyer_name, buyer_country,
                destination_port, origin_port, incoterm, currency, total_value,
                status, hs_codes, ebrc_status, created_by, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            ON CONFLICT (id) DO NOTHING
        """, uuid.UUID(s["id"]), s["shipment_number"], uuid.UUID(s["company_id"]),
            s["buyer_name"], s["buyer_country"], s.get("destination_port"),
            s.get("origin_port"), s.get("incoterm", "FOB"), s.get("currency", "USD"),
            float(s.get("total_value", 0)), s.get("status", "draft"),
            s.get("hs_codes", []), s.get("ebrc_status", "pending"),
            uuid.UUID(s["created_by"]) if s.get("created_by") else None,
            datetime.fromisoformat(s["created_at"].replace("Z", "+00:00")))
    print(f"  Migrated {len(shipments)} shipments")
    
    # 4. Migrate payments
    print("Migrating payments...")
    payments = await mongo_db.payments.find({}, {"_id": 0}).to_list(100000)
    for p in payments:
        await pg.execute("""
            INSERT INTO payments (
                id, shipment_id, company_id, amount, currency, payment_date,
                payment_mode, bank_reference, status, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (id) DO NOTHING
        """, uuid.UUID(p["id"]), uuid.UUID(p["shipment_id"]), uuid.UUID(p["company_id"]),
            float(p.get("amount", 0)), p.get("currency", "USD"),
            datetime.fromisoformat(p["payment_date"]) if p.get("payment_date") else None,
            p.get("payment_mode"), p.get("bank_reference"), p.get("status", "received"),
            datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")))
    print(f"  Migrated {len(payments)} payments")
    
    await pg.close()
    print("Migration completed!")

if __name__ == "__main__":
    asyncio.run(migrate())
```

---

## 8. Deployment Architecture

### Production Setup

```yaml
# docker-compose.yml for Spring Boot
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - DATABASE_URL=jdbc:postgresql://db:5432/exportflow
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=exportflow
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

---

## 9. Testing Strategy

### Migration Testing Checklist

- [ ] Unit tests for all service methods
- [ ] Integration tests for API endpoints
- [ ] Data integrity verification (row counts, checksums)
- [ ] Performance benchmarks (response times)
- [ ] Security testing (IDOR, JWT validation)
- [ ] PII masking verification
- [ ] Export functionality testing

### Test Data Verification Query

```sql
-- Verify migration integrity
SELECT 
    'companies' as table_name, COUNT(*) as row_count FROM companies
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'shipments', COUNT(*) FROM shipments
UNION ALL
SELECT 'payments', COUNT(*) FROM payments;
```

---

## 10. Rollback Plan

### If Migration Fails

1. **Immediate Rollback**: Switch DNS/load balancer back to FastAPI servers
2. **Data Sync**: Run reverse migration script if PostgreSQL had new writes
3. **Monitoring**: Check application logs for errors
4. **Root Cause Analysis**: Document failure points
5. **Retry Strategy**: Fix issues and attempt migration during next maintenance window

### Blue-Green Deployment

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
                             │
            ┌────────────────┴────────────────┐
            │                                 │
            ▼                                 ▼
    ┌───────────────┐                ┌───────────────┐
    │  FastAPI      │                │  Spring Boot  │
    │  (Blue - OLD) │                │  (Green - NEW)│
    │  MongoDB      │                │  PostgreSQL   │
    └───────────────┘                └───────────────┘
    
    Switch traffic: 10% → 50% → 100% over 2 weeks
```

---

## Dependencies (Spring Boot)

```xml
<!-- pom.xml -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
    </dependency>
    <dependency>
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt-api</artifactId>
        <version>0.12.3</version>
    </dependency>
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
    </dependency>
    <dependency>
        <groupId>org.mapstruct</groupId>
        <artifactId>mapstruct</artifactId>
        <version>1.5.5.Final</version>
    </dependency>
</dependencies>
```

---

## Timeline Estimate

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Preparation** | 1-2 weeks | Schema design, environment setup |
| **Backend Migration** | 3-4 weeks | Port all services to Spring Boot |
| **Data Migration** | 1 week | Run migration scripts, verify integrity |
| **Testing** | 2 weeks | Full regression testing |
| **Parallel Run** | 2 weeks | Both systems running, traffic splitting |
| **Cutover** | 1 day | Full switch to new system |
| **Monitoring** | 2 weeks | Post-migration observation |

**Total: 10-12 weeks**

---

## Contact & Support

For questions about this migration guide:
- Technical Lead: [Your Team]
- DevOps: [Infrastructure Team]
- Database Admin: [DBA Team]

---

*Document Version: 1.0*
*Last Updated: February 2025*

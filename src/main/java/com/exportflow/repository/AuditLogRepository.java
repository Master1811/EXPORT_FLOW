package com.exportflow.repository;

import com.exportflow.entity.AuditLog;
import org.springframework.data.domain.Pageable;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface AuditLogRepository extends MongoRepository<AuditLog, String> {

    List<AuditLog> findByOrderByTimestampDesc(Pageable pageable);
}

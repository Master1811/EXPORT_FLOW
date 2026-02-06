package com.exportflow.repository;

import com.exportflow.entity.Compliance;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface ComplianceRepository extends MongoRepository<Compliance, String> {

    Optional<Compliance> findByCompanyIdAndType(String companyId, String type);
}

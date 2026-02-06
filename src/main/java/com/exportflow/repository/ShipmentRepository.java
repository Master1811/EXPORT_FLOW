package com.exportflow.repository;

import com.exportflow.entity.Shipment;
import org.springframework.data.domain.Pageable;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface ShipmentRepository extends MongoRepository<Shipment, String> {

    List<Shipment> findByCompanyId(String companyId, Pageable pageable);

    List<Shipment> findByCompanyIdAndStatus(String companyId, String status, Pageable pageable);
}

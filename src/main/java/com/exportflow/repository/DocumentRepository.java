package com.exportflow.repository;

import com.exportflow.entity.DocumentEntity;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface DocumentRepository extends MongoRepository<DocumentEntity, String> {

    List<DocumentEntity> findByShipmentId(String shipmentId);
}

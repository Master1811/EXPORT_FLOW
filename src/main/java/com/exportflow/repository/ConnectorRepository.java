package com.exportflow.repository;

import com.exportflow.entity.Connector;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface ConnectorRepository extends MongoRepository<Connector, String> {
}

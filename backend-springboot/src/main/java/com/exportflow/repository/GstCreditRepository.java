package com.exportflow.repository;

import com.exportflow.entity.GstCredit;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface GstCreditRepository extends MongoRepository<GstCredit, String> {
}

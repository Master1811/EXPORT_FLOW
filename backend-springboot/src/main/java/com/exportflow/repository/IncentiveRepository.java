package com.exportflow.repository;

import com.exportflow.entity.Incentive;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface IncentiveRepository extends MongoRepository<Incentive, String> {

    List<Incentive> findByCompanyId(String companyId);
}

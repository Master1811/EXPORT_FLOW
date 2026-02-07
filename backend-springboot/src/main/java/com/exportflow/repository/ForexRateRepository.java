package com.exportflow.repository;

import com.exportflow.entity.ForexRate;
import org.springframework.data.mongodb.repository.MongoRepository;

import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.Optional;

public interface ForexRateRepository extends MongoRepository<ForexRate, String> {

    Optional<ForexRate> findFirstByCurrencyOrderByTimestampDesc(String currency);

    List<ForexRate> findByCurrencyOrderByTimestampDesc(String currency, Pageable pageable);
}

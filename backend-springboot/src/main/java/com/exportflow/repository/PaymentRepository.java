package com.exportflow.repository;

import com.exportflow.entity.Payment;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface PaymentRepository extends MongoRepository<Payment, String> {

    List<Payment> findByShipmentId(String shipmentId);

    List<Payment> findByCompanyId(String companyId);

    List<Payment> findByBuyerId(String buyerId);
}

package com.exportflow.service;

import com.exportflow.dto.payment.PaymentCreateRequest;
import com.exportflow.dto.payment.PaymentResponse;
import com.exportflow.entity.Payment;
import com.exportflow.entity.Shipment;
import com.exportflow.repository.PaymentRepository;
import com.exportflow.repository.ShipmentRepository;
import com.exportflow.security.CurrentUser;
import com.exportflow.util.IdUtils;
import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PaymentService {

    private final PaymentRepository paymentRepository;
    private final ShipmentRepository shipmentRepository;

    @Transactional
    public PaymentResponse create(PaymentCreateRequest data, CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        String paymentId = IdUtils.generateId();
        Payment p = new Payment();
        p.setId(paymentId);
        p.setShipmentId(data.getShipmentId());
        p.setAmount(data.getAmount());
        p.setCurrency(data.getCurrency());
        p.setPaymentDate(data.getPaymentDate());
        p.setPaymentMode(data.getPaymentMode());
        p.setBankReference(data.getBankReference());
        p.setExchangeRate(data.getExchangeRate());
        p.setInrAmount(data.getInrAmount());
        p.setStatus("received");
        p.setCompanyId(companyId);
        p.setCreatedBy(user.getId());
        p.setCreatedAt(DateTimeUtils.nowIso());
        paymentRepository.save(p);
        return toResponse(p);
    }

    public List<PaymentResponse> getByShipment(String shipmentId) {
        return paymentRepository.findByShipmentId(shipmentId).stream()
            .map(this::toResponse)
            .collect(Collectors.toList());
    }

    public List<Map<String, Object>> getReceivables(CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        List<Shipment> shipments = shipmentRepository.findByCompanyId(companyId, PageRequest.of(0, 500));
        List<Map<String, Object>> receivables = new ArrayList<>();
        for (Shipment s : shipments) {
            if ("paid".equals(s.getStatus())) continue;
            List<Payment> payments = paymentRepository.findByShipmentId(s.getId());
            double totalPaid = payments.stream().mapToDouble(p -> p.getAmount() != null ? p.getAmount() : 0).sum();
            double outstanding = (s.getTotalValue() != null ? s.getTotalValue() : 0) - totalPaid;
            if (outstanding > 0) {
                Map<String, Object> r = new HashMap<>();
                r.put("shipment_id", s.getId());
                r.put("shipment_number", s.getShipmentNumber());
                r.put("buyer_name", s.getBuyerName());
                r.put("total_value", s.getTotalValue());
                r.put("currency", s.getCurrency());
                r.put("paid", totalPaid);
                r.put("outstanding", outstanding);
                r.put("status", s.getStatus());
                receivables.add(r);
            }
        }
        return receivables;
    }

    public Map<String, Double> getAging(CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        List<Shipment> shipments = shipmentRepository.findByCompanyId(companyId, PageRequest.of(0, 500));
        Map<String, Double> aging = new HashMap<>();
        aging.put("current", 0.0);
        aging.put("30_days", 0.0);
        aging.put("60_days", 0.0);
        aging.put("90_days", 0.0);
        aging.put("over_90", 0.0);
        Instant now = Instant.now();
        for (Shipment s : shipments) {
            List<Payment> payments = paymentRepository.findByShipmentId(s.getId());
            double totalPaid = payments.stream().mapToDouble(p -> p.getAmount() != null ? p.getAmount() : 0).sum();
            double outstanding = (s.getTotalValue() != null ? s.getTotalValue() : 0) - totalPaid;
            if (outstanding > 0 && s.getCreatedAt() != null) {
                try {
                    Instant created = Instant.parse(s.getCreatedAt().replace("Z", "+00:00"));
                    long days = (now.getEpochSecond() - created.getEpochSecond()) / 86400;
                    if (days <= 30) aging.put("current", aging.get("current") + outstanding);
                    else if (days <= 60) aging.put("30_days", aging.get("30_days") + outstanding);
                    else if (days <= 90) aging.put("60_days", aging.get("60_days") + outstanding);
                    else if (days <= 120) aging.put("90_days", aging.get("90_days") + outstanding);
                    else aging.put("over_90", aging.get("over_90") + outstanding);
                } catch (Exception ignored) {}
            }
        }
        return aging;
    }

    private PaymentResponse toResponse(Payment p) {
        return PaymentResponse.builder()
            .id(p.getId())
            .shipmentId(p.getShipmentId())
            .amount(p.getAmount())
            .currency(p.getCurrency())
            .paymentDate(p.getPaymentDate())
            .paymentMode(p.getPaymentMode())
            .bankReference(p.getBankReference())
            .exchangeRate(p.getExchangeRate())
            .inrAmount(p.getInrAmount())
            .status(p.getStatus())
            .createdAt(p.getCreatedAt())
            .build();
    }
}

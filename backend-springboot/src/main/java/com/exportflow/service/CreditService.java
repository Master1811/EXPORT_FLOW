package com.exportflow.service;

import com.exportflow.entity.Payment;
import com.exportflow.entity.Shipment;
import com.exportflow.repository.PaymentRepository;
import com.exportflow.repository.ShipmentRepository;
import com.exportflow.security.CurrentUser;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class CreditService {

    private final PaymentRepository paymentRepository;
    private final ShipmentRepository shipmentRepository;

    public Map<String, Object> getBuyerScore(String buyerId, CurrentUser user) {
        List<Payment> payments = paymentRepository.findByBuyerId(buyerId);
        long onTime = payments.stream().filter(p -> "on_time".equals(p.getStatus())).count();
        long delayed = payments.stream().filter(p -> "delayed".equals(p.getStatus())).count();
        int total = payments.size();
        int score = total == 0 ? 750 : (int) (500 + (onTime / (double) Math.max(total, 1)) * 350);
        String riskLevel = score >= 700 ? "low" : score >= 500 ? "medium" : "high";
        return Map.of(
            "buyer_id", buyerId,
            "buyer_name", "Sample Buyer",
            "credit_score", score,
            "risk_level", riskLevel,
            "payment_history", Map.of("on_time", onTime, "delayed", delayed, "total", total),
            "recommendation", "low".equals(riskLevel) ? "Safe to extend credit" : "Recommend advance payment terms"
        );
    }

    public Map<String, Object> getCompanyScore(CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        List<Shipment> shipments = shipmentRepository.findByCompanyId(companyId, PageRequest.of(0, 500));
        double totalExportValue = shipments.stream().mapToDouble(s -> s.getTotalValue() != null ? s.getTotalValue() : 0).sum();
        return Map.of(
            "company_score", 780,
            "factors", Map.of(
                "export_volume", Map.of("score", 85, "trend", "up"),
                "payment_collection", Map.of("score", 78, "trend", "stable"),
                "compliance_history", Map.of("score", 90, "trend", "up"),
                "buyer_diversity", Map.of("score", 70, "trend", "stable")
            ),
            "credit_limit_eligible", totalExportValue * 0.5,
            "recommendations", List.of("Apply for export credit guarantee", "Consider ECGC coverage")
        );
    }

    public Map<String, Object> getPaymentBehavior(CurrentUser user) {
        return Map.of(
            "average_collection_days", 45,
            "on_time_percentage", 78,
            "trend", "improving",
            "by_region", Map.of(
                "USA", Map.of("avg_days", 38, "on_time", 85),
                "Europe", Map.of("avg_days", 42, "on_time", 80),
                "Middle East", Map.of("avg_days", 55, "on_time", 65)
            )
        );
    }
}

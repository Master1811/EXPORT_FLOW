package com.exportflow.service;

import com.exportflow.entity.Shipment;
import com.exportflow.repository.ShipmentRepository;
import com.exportflow.security.CurrentUser;
import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class AIService {

    private final ShipmentRepository shipmentRepository;

    /**
     * AI query: Python used Emergent LLM. For drop-in replacement, return same structure.
     * Integrate your LLM (e.g. OpenAI, Gemini HTTP) here if needed.
     */
    public Map<String, Object> query(String query, CurrentUser user) {
        try {
            // Placeholder: return same structure as Python. Replace with actual LLM call.
            String response = "I apologize, but I'm currently unable to process your query. Please try again later.";
            return Map.of(
                "query", query,
                "response", response,
                "timestamp", DateTimeUtils.nowIso()
            );
        } catch (Exception e) {
            return Map.of(
                "query", query,
                "response", "I apologize, but I'm currently unable to process your query. Please try again later.",
                "timestamp", DateTimeUtils.nowIso()
            );
        }
    }

    public Map<String, Object> getRefundForecast(CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        List<Shipment> shipments = shipmentRepository.findByCompanyId(companyId, PageRequest.of(0, 500));
        double totalValue = shipments.stream().mapToDouble(s -> s.getTotalValue() != null ? s.getTotalValue() : 0).sum();
        return Map.of(
            "forecast", List.of(
                Map.of("month", "Jan 2025", "expected_refund", totalValue * 0.02, "confidence", 0.85),
                Map.of("month", "Feb 2025", "expected_refund", totalValue * 0.025, "confidence", 0.80),
                Map.of("month", "Mar 2025", "expected_refund", totalValue * 0.03, "confidence", 0.75)
            ),
            "total_expected", totalValue * 0.075,
            "notes", "Based on historical filing patterns and current pending applications"
        );
    }

    public Map<String, Object> getCashflowForecast(CurrentUser user) {
        return Map.of(
            "forecast", List.of(
                Map.of("month", "Jan 2025", "inflow", 2500000, "outflow", 1800000, "net", 700000),
                Map.of("month", "Feb 2025", "inflow", 2800000, "outflow", 2000000, "net", 800000),
                Map.of("month", "Mar 2025", "inflow", 3200000, "outflow", 2200000, "net", 1000000)
            ),
            "alerts", List.of(Map.of("type", "warning", "message", "Large payment due in Feb from Buyer XYZ - monitor closely"))
        );
    }

    public Map<String, Object> getIncentiveOptimizer(CurrentUser user) {
        return Map.of(
            "recommendations", List.of(
                Map.of("action", "Apply for RoDTEP", "shipments_affected", 5, "potential_benefit", 125000, "priority", "high"),
                Map.of("action", "Update HS codes for better rates", "shipments_affected", 3, "potential_benefit", 45000, "priority", "medium")
            ),
            "total_opportunity", 170000
        );
    }

    public Map<String, Object> getRiskAlerts(CurrentUser user) {
        return Map.of(
            "alerts", List.of(
                Map.of("severity", "high", "type", "payment_delay", "message", "Buyer ABC Corp - 3 invoices overdue by 45+ days", "action", "Follow up immediately"),
                Map.of("severity", "medium", "type", "forex", "message", "USD weakening - consider hedging open positions", "action", "Review forex strategy"),
                Map.of("severity", "low", "type", "compliance", "message", "LUT renewal due in 45 days", "action", "Plan renewal")
            )
        );
    }
}

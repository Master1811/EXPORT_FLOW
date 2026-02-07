package com.exportflow.controller;

import com.exportflow.entity.Incentive;
import com.exportflow.entity.Payment;
import com.exportflow.entity.Shipment;
import com.exportflow.repository.IncentiveRepository;
import com.exportflow.repository.PaymentRepository;
import com.exportflow.repository.ShipmentRepository;
import com.exportflow.security.CurrentUser;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final ShipmentRepository shipmentRepository;
    private final PaymentRepository paymentRepository;
    private final IncentiveRepository incentiveRepository;

    @GetMapping("/stats")
    public Map<String, Object> getDashboardStats(@AuthenticationPrincipal CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        List<Shipment> shipments = shipmentRepository.findByCompanyId(companyId, PageRequest.of(0, 500));
        List<Payment> payments = paymentRepository.findByCompanyId(companyId);
        List<Incentive> incentives = incentiveRepository.findByCompanyId(companyId);

        double totalExportValue = shipments.stream().mapToDouble(s -> s.getTotalValue() != null ? s.getTotalValue() : 0).sum();
        double totalPayments = payments.stream().mapToDouble(p -> p.getAmount() != null ? p.getAmount() : 0).sum();
        double totalIncentives = incentives.stream().mapToDouble(i -> i.getIncentiveAmount() != null ? i.getIncentiveAmount() : 0).sum();
        long activeShipments = shipments.stream().filter(s -> s.getStatus() != null && !"completed".equals(s.getStatus()) && !"cancelled".equals(s.getStatus())).count();

        return Map.of(
            "total_export_value", totalExportValue,
            "total_receivables", totalExportValue - totalPayments,
            "total_payments_received", totalPayments,
            "total_incentives_earned", totalIncentives,
            "active_shipments", activeShipments,
            "total_shipments", shipments.size(),
            "pending_gst_refund", totalExportValue * 0.18 * 0.4,
            "compliance_score", 85
        );
    }

    @GetMapping("/charts/export-trend")
    public Map<String, Object> getExportTrend() {
        return Map.of(
            "labels", List.of("Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
            "data", List.of(450000, 520000, 480000, 610000, 580000, 720000)
        );
    }

    @GetMapping("/charts/payment-status")
    public Map<String, Object> getPaymentStatusChart() {
        return Map.of(
            "labels", List.of("Received", "Pending", "Overdue"),
            "data", List.of(65, 25, 10)
        );
    }
}

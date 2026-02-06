package com.exportflow.service;

import com.exportflow.dto.gst.GstInputCreditCreateRequest;
import com.exportflow.dto.gst.GstSummaryResponse;
import com.exportflow.entity.Compliance;
import com.exportflow.entity.GstCredit;
import com.exportflow.entity.Shipment;
import com.exportflow.repository.ComplianceRepository;
import com.exportflow.repository.GstCreditRepository;
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
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class GstService {

    private final GstCreditRepository gstCreditRepository;
    private final ComplianceRepository complianceRepository;
    private final ShipmentRepository shipmentRepository;

    @Transactional
    public Map<String, Object> addInputCredit(GstInputCreditCreateRequest data, CurrentUser user) {
        String creditId = IdUtils.generateId();
        GstCredit c = new GstCredit();
        c.setId(creditId);
        c.setInvoiceNumber(data.getInvoiceNumber());
        c.setSupplierGstin(data.getSupplierGstin());
        c.setInvoiceDate(data.getInvoiceDate());
        c.setTaxableValue(data.getTaxableValue());
        c.setIgst(data.getIgst() != null ? data.getIgst() : 0.0);
        c.setCgst(data.getCgst() != null ? data.getCgst() : 0.0);
        c.setSgst(data.getSgst() != null ? data.getSgst() : 0.0);
        c.setTotalTax(data.getTotalTax());
        c.setCompanyId(user.getCompanyId() != null ? user.getCompanyId() : user.getId());
        c.setStatus("pending");
        c.setCreatedAt(DateTimeUtils.nowIso());
        gstCreditRepository.save(c);
        return Map.of("id", creditId, "message", "GST input credit added");
    }

    public List<GstSummaryResponse> getMonthlySummary(CurrentUser user, Integer year) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        int y = year != null ? year : java.time.Year.now().getValue();
        List<GstSummaryResponse> months = new java.util.ArrayList<>();
        for (int m = 1; m <= 12; m++) {
            String monthStr = String.format("%d-%02d", y, m);
            List<Shipment> shipments = shipmentRepository.findByCompanyId(companyId, PageRequest.of(0, 500));
            double totalValue = shipments.stream()
                .filter(s -> s.getCreatedAt() != null && s.getCreatedAt().startsWith(monthStr))
                .mapToDouble(s -> s.getTotalValue() != null ? s.getTotalValue() : 0)
                .sum();
            double igstPaid = totalValue * 0.18;
            months.add(GstSummaryResponse.builder()
                .month(monthStr)
                .totalExportValue(totalValue)
                .totalIgstPaid(igstPaid)
                .refundEligible(igstPaid)
                .refundClaimed(igstPaid * 0.6)
                .refundPending(igstPaid * 0.4)
                .build());
        }
        return months;
    }

    public Map<String, Object> getExpectedRefund(CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        List<Shipment> shipments = shipmentRepository.findByCompanyId(companyId, PageRequest.of(0, 500));
        double totalExportValue = shipments.stream()
            .mapToDouble(s -> s.getTotalValue() != null ? s.getTotalValue() : 0)
            .sum();
        double expectedRefund = totalExportValue * 0.18 * 0.4;
        String estimatedDate = Instant.now().plus(45, ChronoUnit.DAYS).toString();
        return Map.of(
            "total_export_value", totalExportValue,
            "igst_paid", totalExportValue * 0.18,
            "refund_claimed", totalExportValue * 0.18 * 0.6,
            "refund_expected", expectedRefund,
            "estimated_date", estimatedDate
        );
    }

    public Map<String, Object> getRefundStatus(CurrentUser user) {
        return Map.of(
            "pending_applications", 3,
            "total_pending_amount", 245000,
            "applications", List.of(
                Map.of("ref_number", "GST-REF-2024-001", "amount", 85000, "status", "processing", "filed_date", "2024-01-15"),
                Map.of("ref_number", "GST-REF-2024-002", "amount", 92000, "status", "under_review", "filed_date", "2024-01-28"),
                Map.of("ref_number", "GST-REF-2024-003", "amount", 68000, "status", "approved", "filed_date", "2024-02-10")
            )
        );
    }

    public Map<String, Object> getLutStatus(CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        return complianceRepository.findByCompanyIdAndType(companyId, "lut")
            .map(lut -> {
                Map<String, Object> m = new HashMap<>();
                m.put("id", lut.getId());
                m.put("company_id", lut.getCompanyId());
                m.put("type", lut.getType());
                m.put("lut_number", lut.getLutNumber());
                m.put("financial_year", lut.getFinancialYear());
                m.put("valid_from", lut.getValidFrom());
                m.put("valid_until", lut.getValidUntil());
                m.put("status", lut.getStatus());
                m.put("created_at", lut.getCreatedAt());
                return m;
            })
            .orElse(Map.of(
                "status", "not_filed",
                "message", "LUT not filed for current financial year",
                "action_required", true
            ));
    }

    @Transactional
    public Map<String, Object> linkLut(Map<String, String> data, CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        Compliance lut = new Compliance();
        lut.setId(IdUtils.generateId());
        lut.setCompanyId(companyId);
        lut.setType("lut");
        lut.setLutNumber(data.get("lut_number"));
        lut.setFinancialYear(data.getOrDefault("financial_year", "2024-25"));
        lut.setValidFrom(data.get("valid_from"));
        lut.setValidUntil(data.get("valid_until"));
        lut.setStatus("active");
        lut.setCreatedAt(DateTimeUtils.nowIso());
        complianceRepository.save(lut);
        return Map.of("message", "LUT linked successfully", "lut_number", data.get("lut_number") != null ? data.get("lut_number") : "");
    }
}

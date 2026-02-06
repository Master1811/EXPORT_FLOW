package com.exportflow.service;

import com.exportflow.dto.incentive.IncentiveCalculateRequest;
import com.exportflow.dto.incentive.IncentiveResponse;
import com.exportflow.entity.Incentive;
import com.exportflow.entity.Shipment;
import com.exportflow.repository.IncentiveRepository;
import com.exportflow.repository.ShipmentRepository;
import com.exportflow.security.CurrentUser;
import com.exportflow.util.IdUtils;
import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class IncentiveService {

    private static final Map<String, Double> RODTEP_RATES = Map.of(
        "61", 4.0, "62", 4.0, "63", 4.0,
        "84", 2.5, "85", 2.5,
        "87", 3.0,
        "90", 2.0,
        "94", 3.5
    );

    private final IncentiveRepository incentiveRepository;
    private final ShipmentRepository shipmentRepository;

    public Map<String, Object> checkEligibility(String hsCode) {
        String chapter = hsCode.length() >= 2 ? hsCode.substring(0, 2) : "00";
        double rate = RODTEP_RATES.getOrDefault(chapter, 0.0);
        return Map.of(
            "hs_code", hsCode,
            "chapter", chapter,
            "eligible", rate > 0,
            "rate_percent", rate,
            "scheme", "RoDTEP",
            "notes", rate > 0 ? "Chapter " + chapter + " products eligible for " + rate + "% RoDTEP benefit" : "Not eligible for RoDTEP"
        );
    }

    @Transactional
    public IncentiveResponse calculate(IncentiveCalculateRequest data, CurrentUser user) {
        String primaryHs = (data.getHsCodes() != null && !data.getHsCodes().isEmpty())
            ? data.getHsCodes().get(0) : "00";
        String chapter = primaryHs.length() >= 2 ? primaryHs.substring(0, 2) : "00";
        double rate = RODTEP_RATES.getOrDefault(chapter, 0.0);
        double totalIncentive = data.getFobValue() * (rate / 100);
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        String incentiveId = IdUtils.generateId();
        Incentive inv = new Incentive();
        inv.setId(incentiveId);
        inv.setShipmentId(data.getShipmentId());
        inv.setScheme("RoDTEP");
        inv.setHsCode(primaryHs);
        inv.setFobValue(data.getFobValue());
        inv.setRatePercent(rate);
        inv.setIncentiveAmount(totalIncentive);
        inv.setStatus("calculated");
        inv.setCompanyId(companyId);
        inv.setCreatedAt(DateTimeUtils.nowIso());
        incentiveRepository.save(inv);
        return IncentiveResponse.builder()
            .id(inv.getId())
            .shipmentId(inv.getShipmentId())
            .scheme(inv.getScheme())
            .hsCode(inv.getHsCode())
            .fobValue(inv.getFobValue())
            .ratePercent(inv.getRatePercent())
            .incentiveAmount(inv.getIncentiveAmount())
            .status(inv.getStatus())
            .createdAt(inv.getCreatedAt())
            .build();
    }

    public Map<String, Object> getLostMoney(CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        List<Shipment> shipments = shipmentRepository.findByCompanyId(companyId, PageRequest.of(0, 500));
        Set<String> claimedShipmentIds = incentiveRepository.findByCompanyId(companyId).stream()
            .map(Incentive::getShipmentId)
            .collect(Collectors.toSet());
        List<Shipment> unclaimed = shipments.stream()
            .filter(s -> !claimedShipmentIds.contains(s.getId()))
            .toList();
        double potentialLoss = unclaimed.stream()
            .mapToDouble(s -> (s.getTotalValue() != null ? s.getTotalValue() : 0) * 0.03)
            .sum();
        return Map.of(
            "unclaimed_shipments", unclaimed.size(),
            "potential_incentive_loss", potentialLoss,
            "recommendation", "Claim incentives for " + unclaimed.size() + " shipments to recover ₹" + String.format("%,.2f", potentialLoss)
        );
    }

    public Map<String, Object> getSummary(CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        List<Incentive> incentives = incentiveRepository.findByCompanyId(companyId);
        double total = incentives.stream().mapToDouble(i -> i.getIncentiveAmount() != null ? i.getIncentiveAmount() : 0).sum();
        double claimed = incentives.stream().filter(i -> "claimed".equals(i.getStatus())).mapToDouble(i -> i.getIncentiveAmount() != null ? i.getIncentiveAmount() : 0).sum();
        double pending = incentives.stream().filter(i -> List.of("calculated", "submitted").contains(i.getStatus())).mapToDouble(i -> i.getIncentiveAmount() != null ? i.getIncentiveAmount() : 0).sum();
        double rodtep = incentives.stream().filter(i -> "RoDTEP".equals(i.getScheme())).mapToDouble(i -> i.getIncentiveAmount() != null ? i.getIncentiveAmount() : 0).sum();
        double rosctl = incentives.stream().filter(i -> "RoSCTL".equals(i.getScheme())).mapToDouble(i -> i.getIncentiveAmount() != null ? i.getIncentiveAmount() : 0).sum();
        Map<String, Double> byScheme = new HashMap<>();
        byScheme.put("RoDTEP", rodtep);
        byScheme.put("RoSCTL", rosctl);
        return Map.of(
            "total_incentives", total,
            "claimed", claimed,
            "pending", pending,
            "count", incentives.size(),
            "by_scheme", byScheme
        );
    }
}

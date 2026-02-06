package com.exportflow.service;

import com.exportflow.entity.Connector;
import com.exportflow.repository.ConnectorRepository;
import com.exportflow.security.CurrentUser;
import com.exportflow.util.IdUtils;
import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class ConnectorService {

    private final ConnectorRepository connectorRepository;

    @Transactional
    public Map<String, Object> initiateBank(Map<String, Object> data, CurrentUser user) {
        String jobId = IdUtils.generateId();
        String id = IdUtils.generateId();
        Connector c = new Connector();
        c.setId(id);
        c.setJobId(jobId);
        c.setConnectorType("bank");
        c.setCompanyId(user.getCompanyId() != null ? user.getCompanyId() : user.getId());
        c.setStatus("initiating");
        c.setCreatedAt(DateTimeUtils.nowIso());
        connectorRepository.save(c);
        return Map.of(
            "job_id", jobId,
            "status", "initiating",
            "message", "Bank connection initiated via Account Aggregator"
        );
    }

    public Map<String, Object> bankConsent(Map<String, Object> data, CurrentUser user) {
        return Map.of(
            "status", "consent_pending",
            "consent_url", "https://aa.example.com/consent",
            "expires_in", 300
        );
    }

    public Map<String, Object> syncBank(CurrentUser user) {
        return Map.of(
            "status", "synced",
            "last_sync", DateTimeUtils.nowIso(),
            "accounts", java.util.List.of(
                Map.of("account_number", "****1234", "bank", "HDFC Bank", "balance", 1250000, "type", "current"),
                Map.of("account_number", "****5678", "bank", "ICICI Bank", "balance", 850000, "type", "EEFC")
            )
        );
    }

    @Transactional
    public Map<String, Object> linkGst(Map<String, Object> data, CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        String gstin = data != null && data.get("gstin") != null ? data.get("gstin").toString() : null;
        Connector c = new Connector();
        c.setId(IdUtils.generateId());
        c.setCompanyId(companyId);
        c.setGstin(gstin);
        c.setConnectorType("gst");
        c.setStatus("linked");
        c.setCreatedAt(DateTimeUtils.nowIso());
        connectorRepository.save(c);
        return Map.of("status", "linked", "gstin", gstin);
    }

    public Map<String, Object> syncGst(CurrentUser user) {
        return Map.of(
            "status", "synced",
            "last_sync", DateTimeUtils.nowIso(),
            "data", Map.of(
                "gstr1_filed", true,
                "gstr3b_filed", true,
                "pending_returns", java.util.List.of(),
                "input_credit_balance", 125000
            )
        );
    }

    @Transactional
    public Map<String, Object> linkCustoms(Map<String, Object> data, CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        String iecCode = data != null && data.get("iec_code") != null ? data.get("iec_code").toString() : null;
        Connector c = new Connector();
        c.setId(IdUtils.generateId());
        c.setCompanyId(companyId);
        c.setIecCode(iecCode);
        c.setConnectorType("customs");
        c.setStatus("linked");
        c.setCreatedAt(DateTimeUtils.nowIso());
        connectorRepository.save(c);
        return Map.of("status", "linked", "iec_code", iecCode);
    }

    public Map<String, Object> syncCustoms(CurrentUser user) {
        return Map.of(
            "status", "synced",
            "last_sync", DateTimeUtils.nowIso(),
            "data", Map.of(
                "shipping_bills", 45,
                "pending_assessments", 2,
                "duty_drawback_pending", 75000
            )
        );
    }
}

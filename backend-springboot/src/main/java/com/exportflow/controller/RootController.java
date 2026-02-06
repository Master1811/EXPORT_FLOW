package com.exportflow.controller;

import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequiredArgsConstructor
public class RootController {

    private final com.exportflow.repository.AuditLogRepository auditLogRepository;

    @GetMapping("")
    public Map<String, String> root() {
        return Map.of(
            "message", "Exporter Finance & Compliance Platform API",
            "version", "1.0.0"
        );
    }

    @GetMapping("/health")
    public Map<String, String> healthCheck() {
        return Map.of(
            "status", "healthy",
            "timestamp", DateTimeUtils.nowIso()
        );
    }

    @GetMapping("/metrics")
    public Map<String, Object> getMetrics() {
        return Map.of(
            "uptime", "99.9%",
            "requests_today", 1250,
            "avg_response_time", "45ms"
        );
    }

    @GetMapping("/audit/logs")
    public List<Map<String, Object>> getAuditLogs(@RequestParam(defaultValue = "100") int limit) {
        return auditLogRepository.findByOrderByTimestampDesc(org.springframework.data.domain.PageRequest.of(0, limit))
            .stream()
            .map(a -> {
                java.util.Map<String, Object> m = new java.util.HashMap<>();
                m.put("timestamp", a.getTimestamp() != null ? a.getTimestamp() : "");
                m.put("data", a.getData() != null ? a.getData() : Map.of());
                if (a.getId() != null) m.put("id", a.getId());
                return m;
            })
            .toList();
    }
}

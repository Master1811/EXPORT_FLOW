package com.exportflow.controller;

import com.exportflow.dto.ai.AIQueryRequest;
import com.exportflow.security.CurrentUser;
import com.exportflow.service.AIService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/ai")
@RequiredArgsConstructor
public class AIController {

    private final AIService aiService;

    @PostMapping("/query")
    public Map<String, Object> aiQuery(@Valid @RequestBody AIQueryRequest data, @AuthenticationPrincipal CurrentUser user) {
        return aiService.query(data.getQuery(), user);
    }

    @GetMapping("/refund-forecast")
    public Map<String, Object> getRefundForecast(@AuthenticationPrincipal CurrentUser user) {
        return aiService.getRefundForecast(user);
    }

    @GetMapping("/cashflow-forecast")
    public Map<String, Object> getCashflowForecast(@AuthenticationPrincipal CurrentUser user) {
        return aiService.getCashflowForecast(user);
    }

    @GetMapping("/incentive-optimizer")
    public Map<String, Object> getIncentiveOptimizer(@AuthenticationPrincipal CurrentUser user) {
        return aiService.getIncentiveOptimizer(user);
    }

    @GetMapping("/risk-alerts")
    public Map<String, Object> getRiskAlerts(@AuthenticationPrincipal CurrentUser user) {
        return aiService.getRiskAlerts(user);
    }
}

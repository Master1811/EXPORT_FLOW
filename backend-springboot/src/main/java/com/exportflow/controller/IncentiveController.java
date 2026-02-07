package com.exportflow.controller;

import com.exportflow.dto.incentive.IncentiveCalculateRequest;
import com.exportflow.dto.incentive.IncentiveResponse;
import com.exportflow.security.CurrentUser;
import com.exportflow.service.IncentiveService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/incentives")
@RequiredArgsConstructor
public class IncentiveController {

    private final IncentiveService incentiveService;

    @GetMapping("/rodtep-eligibility")
    public Map<String, Object> checkRodtepEligibility(@RequestParam("hs_code") String hsCode) {
        return incentiveService.checkEligibility(hsCode);
    }

    @PostMapping("/calculate")
    public IncentiveResponse calculate(@Valid @RequestBody IncentiveCalculateRequest data, @AuthenticationPrincipal CurrentUser user) {
        return incentiveService.calculate(data, user);
    }

    @GetMapping("/lost-money")
    public Map<String, Object> getLostIncentives(@AuthenticationPrincipal CurrentUser user) {
        return incentiveService.getLostMoney(user);
    }

    @GetMapping("/summary")
    public Map<String, Object> getSummary(@AuthenticationPrincipal CurrentUser user) {
        return incentiveService.getSummary(user);
    }
}

package com.exportflow.controller;

import com.exportflow.security.CurrentUser;
import com.exportflow.service.CreditService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/credit")
@RequiredArgsConstructor
public class CreditController {

    private final CreditService creditService;

    @GetMapping("/buyer-score/{buyer_id}")
    public Map<String, Object> getBuyerScore(@PathVariable("buyer_id") String buyerId, @AuthenticationPrincipal CurrentUser user) {
        return creditService.getBuyerScore(buyerId, user);
    }

    @GetMapping("/company-score")
    public Map<String, Object> getCompanyScore(@AuthenticationPrincipal CurrentUser user) {
        return creditService.getCompanyScore(user);
    }

    @GetMapping("/payment-behavior")
    public Map<String, Object> getPaymentBehavior(@AuthenticationPrincipal CurrentUser user) {
        return creditService.getPaymentBehavior(user);
    }
}

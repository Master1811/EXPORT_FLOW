package com.exportflow.controller;

import com.exportflow.dto.forex.ForexRateCreateRequest;
import com.exportflow.dto.forex.ForexRateResponse;
import com.exportflow.security.CurrentUser;
import com.exportflow.service.ForexService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/forex")
@RequiredArgsConstructor
public class ForexController {

    private final ForexService forexService;

    @PostMapping("/rate")
    public ForexRateResponse createRate(@Valid @RequestBody ForexRateCreateRequest data, @AuthenticationPrincipal CurrentUser user) {
        return forexService.createRate(data, user);
    }

    @GetMapping("/latest")
    public Map<String, Object> getLatest() {
        return forexService.getLatest();
    }

    @GetMapping("/history/{currency}")
    public Map<String, Object> getHistory(@PathVariable String currency, @RequestParam(defaultValue = "30") int days, @AuthenticationPrincipal CurrentUser user) {
        return forexService.getHistory(currency, days);
    }
}

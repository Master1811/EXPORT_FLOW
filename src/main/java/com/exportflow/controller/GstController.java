package com.exportflow.controller;

import com.exportflow.dto.gst.GstInputCreditCreateRequest;
import com.exportflow.dto.gst.GstSummaryResponse;
import com.exportflow.security.CurrentUser;
import com.exportflow.service.GstService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequiredArgsConstructor
public class GstController {

    private final GstService gstService;

    @PostMapping("/gst/input-credit")
    public Map<String, Object> addGstInputCredit(@Valid @RequestBody GstInputCreditCreateRequest data, @AuthenticationPrincipal CurrentUser user) {
        return gstService.addInputCredit(data, user);
    }

    @GetMapping("/gst/summary/monthly")
    public List<GstSummaryResponse> getGstMonthlySummary(@RequestParam(required = false) Integer year, @AuthenticationPrincipal CurrentUser user) {
        return gstService.getMonthlySummary(user, year);
    }

    @GetMapping("/gst/refund/expected")
    public Map<String, Object> getExpectedRefund(@AuthenticationPrincipal CurrentUser user) {
        return gstService.getExpectedRefund(user);
    }

    @GetMapping("/gst/refund/status")
    public Map<String, Object> getRefundStatus(@AuthenticationPrincipal CurrentUser user) {
        return gstService.getRefundStatus(user);
    }

    @GetMapping("/compliance/lut-status")
    public Map<String, Object> getLutStatus(@AuthenticationPrincipal CurrentUser user) {
        return gstService.getLutStatus(user);
    }

    @PostMapping("/compliance/lut-link")
    public Map<String, Object> linkLut(@RequestBody Map<String, String> data, @AuthenticationPrincipal CurrentUser user) {
        return gstService.linkLut(data, user);
    }
}

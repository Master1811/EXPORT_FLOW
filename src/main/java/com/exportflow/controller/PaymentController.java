package com.exportflow.controller;

import com.exportflow.dto.payment.PaymentCreateRequest;
import com.exportflow.dto.payment.PaymentResponse;
import com.exportflow.security.CurrentUser;
import com.exportflow.service.PaymentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/payments")
@RequiredArgsConstructor
public class PaymentController {

    private final PaymentService paymentService;

    @PostMapping("")
    public PaymentResponse create(@Valid @RequestBody PaymentCreateRequest data, @AuthenticationPrincipal CurrentUser user) {
        return paymentService.create(data, user);
    }

    @GetMapping("/shipment/{shipment_id}")
    public List<PaymentResponse> getByShipment(@PathVariable("shipment_id") String shipmentId, @AuthenticationPrincipal CurrentUser user) {
        return paymentService.getByShipment(shipmentId);
    }

    @GetMapping("/receivables")
    public List<Map<String, Object>> getReceivables(@AuthenticationPrincipal CurrentUser user) {
        return paymentService.getReceivables(user);
    }

    @GetMapping("/receivables/aging")
    public Map<String, Double> getReceivablesAging(@AuthenticationPrincipal CurrentUser user) {
        return paymentService.getAging(user);
    }
}

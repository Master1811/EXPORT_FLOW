package com.exportflow.controller;

import com.exportflow.dto.shipment.ShipmentCreateRequest;
import com.exportflow.dto.shipment.ShipmentResponse;
import com.exportflow.dto.shipment.ShipmentUpdateRequest;
import com.exportflow.security.CurrentUser;
import com.exportflow.service.ShipmentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/shipments")
@RequiredArgsConstructor
public class ShipmentController {

    private final ShipmentService shipmentService;

    @PostMapping("")
    public ShipmentResponse create(@Valid @RequestBody ShipmentCreateRequest data, @AuthenticationPrincipal CurrentUser user) {
        return shipmentService.create(data, user);
    }

    @GetMapping("")
    public List<ShipmentResponse> getAll(
        @RequestParam(required = false) String status,
        @RequestParam(defaultValue = "0") int skip,
        @RequestParam(defaultValue = "50") int limit,
        @AuthenticationPrincipal CurrentUser user
    ) {
        return shipmentService.getAll(user, status, skip, limit);
    }

    @GetMapping("/{shipment_id}")
    public ShipmentResponse get(@PathVariable("shipment_id") String shipmentId) {
        return shipmentService.get(shipmentId);
    }

    @PutMapping("/{shipment_id}")
    public ShipmentResponse update(@PathVariable("shipment_id") String shipmentId, @Valid @RequestBody ShipmentUpdateRequest data, @AuthenticationPrincipal CurrentUser user) {
        return shipmentService.update(shipmentId, data);
    }

    @DeleteMapping("/{shipment_id}")
    public Map<String, String> delete(@PathVariable("shipment_id") String shipmentId, @AuthenticationPrincipal CurrentUser user) {
        shipmentService.delete(shipmentId);
        return Map.of("message", "Shipment deleted");
    }
}

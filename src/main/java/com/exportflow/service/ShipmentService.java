package com.exportflow.service;

import com.exportflow.dto.shipment.ShipmentCreateRequest;
import com.exportflow.dto.shipment.ShipmentResponse;
import com.exportflow.dto.shipment.ShipmentUpdateRequest;
import com.exportflow.entity.Shipment;
import com.exportflow.exception.ResourceNotFoundException;
import com.exportflow.repository.ShipmentRepository;
import com.exportflow.security.CurrentUser;
import com.exportflow.util.IdUtils;
import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ShipmentService {

    private final ShipmentRepository shipmentRepository;

    @Transactional
    public ShipmentResponse create(ShipmentCreateRequest data, CurrentUser user) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        String shipmentId = IdUtils.generateId();
        Shipment s = new Shipment();
        s.setId(shipmentId);
        s.setShipmentNumber(data.getShipmentNumber());
        s.setBuyerName(data.getBuyerName());
        s.setBuyerCountry(data.getBuyerCountry());
        s.setDestinationPort(data.getDestinationPort());
        s.setOriginPort(data.getOriginPort());
        s.setIncoterm(data.getIncoterm() != null ? data.getIncoterm() : "FOB");
        s.setCurrency(data.getCurrency() != null ? data.getCurrency() : "USD");
        s.setTotalValue(data.getTotalValue());
        s.setStatus(data.getStatus() != null ? data.getStatus() : "draft");
        s.setExpectedShipDate(data.getExpectedShipDate());
        s.setProductDescription(data.getProductDescription());
        s.setHsCodes(data.getHsCodes());
        s.setCompanyId(companyId);
        s.setCreatedBy(user.getId());
        String now = DateTimeUtils.nowIso();
        s.setCreatedAt(now);
        s.setUpdatedAt(now);
        shipmentRepository.save(s);
        return toResponse(s);
    }

    public List<ShipmentResponse> getAll(CurrentUser user, String status, int skip, int limit) {
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        List<Shipment> list;
        if (status != null && !status.isBlank()) {
            list = shipmentRepository.findByCompanyIdAndStatus(companyId, status, PageRequest.of(skip / limit, limit));
        } else {
            list = shipmentRepository.findByCompanyId(companyId, PageRequest.of(skip / limit, limit));
        }
        return list.stream().map(this::toResponse).collect(Collectors.toList());
    }

    public ShipmentResponse get(String shipmentId) {
        Shipment s = shipmentRepository.findById(shipmentId)
            .orElseThrow(() -> new ResourceNotFoundException("Shipment not found"));
        return toResponse(s);
    }

    @Transactional
    public ShipmentResponse update(String shipmentId, ShipmentUpdateRequest data) {
        Shipment s = shipmentRepository.findById(shipmentId)
            .orElseThrow(() -> new ResourceNotFoundException("Shipment not found"));
        if (data.getBuyerName() != null) s.setBuyerName(data.getBuyerName());
        if (data.getBuyerCountry() != null) s.setBuyerCountry(data.getBuyerCountry());
        if (data.getDestinationPort() != null) s.setDestinationPort(data.getDestinationPort());
        if (data.getOriginPort() != null) s.setOriginPort(data.getOriginPort());
        if (data.getIncoterm() != null) s.setIncoterm(data.getIncoterm());
        if (data.getCurrency() != null) s.setCurrency(data.getCurrency());
        if (data.getTotalValue() != null) s.setTotalValue(data.getTotalValue());
        if (data.getStatus() != null) s.setStatus(data.getStatus());
        if (data.getExpectedShipDate() != null) s.setExpectedShipDate(data.getExpectedShipDate());
        if (data.getProductDescription() != null) s.setProductDescription(data.getProductDescription());
        if (data.getHsCodes() != null) s.setHsCodes(data.getHsCodes());
        s.setUpdatedAt(DateTimeUtils.nowIso());
        shipmentRepository.save(s);
        return toResponse(s);
    }

    @Transactional
    public void delete(String shipmentId) {
        if (!shipmentRepository.existsById(shipmentId)) {
            throw new ResourceNotFoundException("Shipment not found");
        }
        shipmentRepository.deleteById(shipmentId);
    }

    private ShipmentResponse toResponse(Shipment s) {
        return ShipmentResponse.builder()
            .id(s.getId())
            .shipmentNumber(s.getShipmentNumber())
            .buyerName(s.getBuyerName())
            .buyerCountry(s.getBuyerCountry())
            .destinationPort(s.getDestinationPort())
            .originPort(s.getOriginPort())
            .incoterm(s.getIncoterm())
            .currency(s.getCurrency())
            .totalValue(s.getTotalValue())
            .status(s.getStatus())
            .expectedShipDate(s.getExpectedShipDate())
            .productDescription(s.getProductDescription())
            .hsCodes(s.getHsCodes())
            .companyId(s.getCompanyId())
            .createdAt(s.getCreatedAt())
            .updatedAt(s.getUpdatedAt())
            .build();
    }
}

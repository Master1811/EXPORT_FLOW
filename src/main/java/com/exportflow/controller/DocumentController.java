package com.exportflow.controller;

import com.exportflow.dto.documents.DocumentResponse;
import com.exportflow.dto.documents.InvoiceCreateRequest;
import com.exportflow.security.CurrentUser;
import com.exportflow.service.DocumentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@RestController
@RequiredArgsConstructor
public class DocumentController {

    private final DocumentService documentService;

    @PostMapping("/shipments/{shipment_id}/invoice")
    public DocumentResponse createInvoice(@PathVariable("shipment_id") String shipmentId, @Valid @RequestBody InvoiceCreateRequest data, @AuthenticationPrincipal CurrentUser user) {
        return documentService.createInvoice(shipmentId, data, user);
    }

    @PostMapping("/shipments/{shipment_id}/packing-list")
    public DocumentResponse createPackingList(@PathVariable("shipment_id") String shipmentId, @RequestBody Map<String, Object> data, @AuthenticationPrincipal CurrentUser user) {
        return documentService.createPackingList(shipmentId, data, user);
    }

    @PostMapping("/shipments/{shipment_id}/shipping-bill")
    public DocumentResponse createShippingBill(@PathVariable("shipment_id") String shipmentId, @RequestBody Map<String, Object> data, @AuthenticationPrincipal CurrentUser user) {
        return documentService.createShippingBill(shipmentId, data, user);
    }

    @GetMapping("/shipments/{shipment_id}/documents")
    public List<DocumentResponse> getShipmentDocuments(@PathVariable("shipment_id") String shipmentId, @AuthenticationPrincipal CurrentUser user) {
        return documentService.getShipmentDocuments(shipmentId);
    }

    @PostMapping("/documents/ocr/extract")
    public Map<String, Object> extractDocument(@RequestParam("file") MultipartFile file, @AuthenticationPrincipal CurrentUser user) {
        return documentService.ocrExtract(file.getOriginalFilename() != null ? file.getOriginalFilename() : "file", user);
    }

    @PostMapping("/invoices/bulk-upload")
    public Map<String, Object> bulkUploadInvoices(@RequestParam("files") List<MultipartFile> files, @AuthenticationPrincipal CurrentUser user) {
        return documentService.bulkUpload(files.size(), user);
    }
}

package com.exportflow.service;

import com.exportflow.dto.documents.DocumentResponse;
import com.exportflow.dto.documents.InvoiceCreateRequest;
import com.exportflow.entity.DocumentEntity;
import com.exportflow.entity.Job;
import com.exportflow.exception.ResourceNotFoundException;
import com.exportflow.repository.DocumentRepository;
import com.exportflow.repository.JobRepository;
import com.exportflow.repository.ShipmentRepository;
import com.exportflow.security.CurrentUser;
import com.exportflow.util.IdUtils;
import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class DocumentService {

    private final DocumentRepository documentRepository;
    private final JobRepository jobRepository;
    private final ShipmentRepository shipmentRepository;

    @Transactional
    public DocumentResponse createInvoice(String shipmentId, InvoiceCreateRequest data, CurrentUser user) {
        if (!shipmentRepository.existsById(shipmentId)) {
            throw new ResourceNotFoundException("Shipment not found");
        }
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        String docId = IdUtils.generateId();
        DocumentEntity doc = new DocumentEntity();
        doc.setId(docId);
        doc.setDocumentType("invoice");
        doc.setShipmentId(shipmentId);
        doc.setDocumentNumber(data.getInvoiceNumber());
        Map<String, Object> dataMap = new HashMap<>();
        dataMap.put("invoice_number", data.getInvoiceNumber());
        dataMap.put("invoice_date", data.getInvoiceDate());
        dataMap.put("items", data.getItems());
        dataMap.put("subtotal", data.getSubtotal());
        dataMap.put("tax_amount", data.getTaxAmount());
        dataMap.put("total_amount", data.getTotalAmount());
        dataMap.put("payment_terms", data.getPaymentTerms());
        doc.setData(dataMap);
        doc.setCompanyId(companyId);
        doc.setCreatedBy(user.getId());
        doc.setCreatedAt(DateTimeUtils.nowIso());
        documentRepository.save(doc);
        return toResponse(doc);
    }

    @Transactional
    public DocumentResponse createPackingList(String shipmentId, Map<String, Object> data, CurrentUser user) {
        if (!shipmentRepository.existsById(shipmentId)) {
            throw new ResourceNotFoundException("Shipment not found");
        }
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        String docId = IdUtils.generateId();
        String docNumber = data.containsKey("packing_list_number")
            ? (String) data.get("packing_list_number")
            : "PL-" + shipmentId.substring(0, Math.min(8, shipmentId.length()));
        DocumentEntity doc = new DocumentEntity();
        doc.setId(docId);
        doc.setDocumentType("packing_list");
        doc.setShipmentId(shipmentId);
        doc.setDocumentNumber(docNumber);
        doc.setData(data);
        doc.setCompanyId(companyId);
        doc.setCreatedBy(user.getId());
        doc.setCreatedAt(DateTimeUtils.nowIso());
        documentRepository.save(doc);
        return toResponse(doc);
    }

    @Transactional
    public DocumentResponse createShippingBill(String shipmentId, Map<String, Object> data, CurrentUser user) {
        if (!shipmentRepository.existsById(shipmentId)) {
            throw new ResourceNotFoundException("Shipment not found");
        }
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        String docId = IdUtils.generateId();
        String docNumber = data.containsKey("sb_number")
            ? (String) data.get("sb_number")
            : "SB-" + shipmentId.substring(0, Math.min(8, shipmentId.length()));
        DocumentEntity doc = new DocumentEntity();
        doc.setId(docId);
        doc.setDocumentType("shipping_bill");
        doc.setShipmentId(shipmentId);
        doc.setDocumentNumber(docNumber);
        doc.setData(data);
        doc.setCompanyId(companyId);
        doc.setCreatedBy(user.getId());
        doc.setCreatedAt(DateTimeUtils.nowIso());
        documentRepository.save(doc);
        return toResponse(doc);
    }

    public List<DocumentResponse> getShipmentDocuments(String shipmentId) {
        return documentRepository.findByShipmentId(shipmentId).stream()
            .map(this::toResponse)
            .collect(Collectors.toList());
    }

    private DocumentResponse toResponse(DocumentEntity d) {
        return DocumentResponse.builder()
            .id(d.getId())
            .documentType(d.getDocumentType())
            .shipmentId(d.getShipmentId())
            .documentNumber(d.getDocumentNumber())
            .createdAt(d.getCreatedAt())
            .data(d.getData())
            .build();
    }

    @Transactional
    public Map<String, Object> ocrExtract(String filename, CurrentUser user) {
        String jobId = IdUtils.generateId();
        Job job = new Job();
        job.setId(jobId);
        job.setType("ocr_extraction");
        job.setStatus("processing");
        job.setCompanyId(user.getCompanyId() != null ? user.getCompanyId() : user.getId());
        job.setFilename(filename);
        job.setCreatedAt(DateTimeUtils.nowIso());
        jobRepository.save(job);
        return Map.of(
            "job_id", jobId,
            "status", "processing",
            "message", "Document queued for OCR extraction"
        );
    }

    @Transactional
    public Map<String, Object> bulkUpload(int fileCount, CurrentUser user) {
        String jobId = IdUtils.generateId();
        Job job = new Job();
        job.setId(jobId);
        job.setType("bulk_invoice_upload");
        job.setStatus("processing");
        job.setCompanyId(user.getCompanyId() != null ? user.getCompanyId() : user.getId());
        job.setFileCount(fileCount);
        job.setCreatedAt(DateTimeUtils.nowIso());
        jobRepository.save(job);
        return Map.of(
            "job_id", jobId,
            "status", "processing",
            "files_queued", fileCount
        );
    }
}

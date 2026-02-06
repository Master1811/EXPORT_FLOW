package com.exportflow.dto.documents;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
public class InvoiceCreateRequest {

    @NotBlank
    @JsonProperty("invoice_number")
    private String invoiceNumber;

    @NotBlank
    @JsonProperty("invoice_date")
    private String invoiceDate;

    @NotNull
    private List<Map<String, Object>> items;

    @NotNull
    private Double subtotal;

    @JsonProperty("tax_amount")
    private Double taxAmount = 0.0;

    @JsonProperty("total_amount")
    @NotNull
    private Double totalAmount;

    @JsonProperty("payment_terms")
    private String paymentTerms;
}

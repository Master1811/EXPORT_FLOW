package com.exportflow.dto.gst;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class GstInputCreditCreateRequest {

    @NotBlank
    @JsonProperty("invoice_number")
    private String invoiceNumber;

    @NotBlank
    @JsonProperty("supplier_gstin")
    private String supplierGstin;

    @NotBlank
    @JsonProperty("invoice_date")
    private String invoiceDate;

    @NotNull
    @JsonProperty("taxable_value")
    private Double taxableValue;

    private Double igst = 0.0;
    private Double cgst = 0.0;
    private Double sgst = 0.0;

    @NotNull
    @JsonProperty("total_tax")
    private Double totalTax;
}

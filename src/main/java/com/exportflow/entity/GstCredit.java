package com.exportflow.entity;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

@Document(collection = "gst_credits")
public class GstCredit {

    @Id
    private String id;
    @Field("invoice_number")
    private String invoiceNumber;
    @Field("supplier_gstin")
    private String supplierGstin;
    @Field("invoice_date")
    private String invoiceDate;
    @Field("taxable_value")
    private Double taxableValue;
    private Double igst;
    private Double cgst;
    private Double sgst;
    @Field("total_tax")
    private Double totalTax;
    @Field("company_id")
    private String companyId;
    private String status;
    @Field("created_at")
    private String createdAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getInvoiceNumber() { return invoiceNumber; }
    public void setInvoiceNumber(String invoiceNumber) { this.invoiceNumber = invoiceNumber; }
    public String getSupplierGstin() { return supplierGstin; }
    public void setSupplierGstin(String supplierGstin) { this.supplierGstin = supplierGstin; }
    public String getInvoiceDate() { return invoiceDate; }
    public void setInvoiceDate(String invoiceDate) { this.invoiceDate = invoiceDate; }
    public Double getTaxableValue() { return taxableValue; }
    public void setTaxableValue(Double taxableValue) { this.taxableValue = taxableValue; }
    public Double getIgst() { return igst; }
    public void setIgst(Double igst) { this.igst = igst; }
    public Double getCgst() { return cgst; }
    public void setCgst(Double cgst) { this.cgst = cgst; }
    public Double getSgst() { return sgst; }
    public void setSgst(Double sgst) { this.sgst = sgst; }
    public Double getTotalTax() { return totalTax; }
    public void setTotalTax(Double totalTax) { this.totalTax = totalTax; }
    public String getCompanyId() { return companyId; }
    public void setCompanyId(String companyId) { this.companyId = companyId; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}

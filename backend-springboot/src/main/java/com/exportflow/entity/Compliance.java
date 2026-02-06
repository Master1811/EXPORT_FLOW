package com.exportflow.entity;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

@Document(collection = "compliance")
public class Compliance {

    @Id
    private String id;
    @Field("company_id")
    private String companyId;
    private String type;
    @Field("lut_number")
    private String lutNumber;
    @Field("financial_year")
    private String financialYear;
    @Field("valid_from")
    private String validFrom;
    @Field("valid_until")
    private String validUntil;
    private String status;
    @Field("created_at")
    private String createdAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getCompanyId() { return companyId; }
    public void setCompanyId(String companyId) { this.companyId = companyId; }
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    public String getLutNumber() { return lutNumber; }
    public void setLutNumber(String lutNumber) { this.lutNumber = lutNumber; }
    public String getFinancialYear() { return financialYear; }
    public void setFinancialYear(String financialYear) { this.financialYear = financialYear; }
    public String getValidFrom() { return validFrom; }
    public void setValidFrom(String validFrom) { this.validFrom = validFrom; }
    public String getValidUntil() { return validUntil; }
    public void setValidUntil(String validUntil) { this.validUntil = validUntil; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}

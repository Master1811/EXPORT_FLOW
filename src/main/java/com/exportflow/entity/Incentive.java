package com.exportflow.entity;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

@Document(collection = "incentives")
public class Incentive {

    @Id
    private String id;
    @Field("shipment_id")
    private String shipmentId;
    private String scheme;
    @Field("hs_code")
    private String hsCode;
    @Field("fob_value")
    private Double fobValue;
    @Field("rate_percent")
    private Double ratePercent;
    @Field("incentive_amount")
    private Double incentiveAmount;
    private String status;
    @Field("company_id")
    private String companyId;
    @Field("created_at")
    private String createdAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getShipmentId() { return shipmentId; }
    public void setShipmentId(String shipmentId) { this.shipmentId = shipmentId; }
    public String getScheme() { return scheme; }
    public void setScheme(String scheme) { this.scheme = scheme; }
    public String getHsCode() { return hsCode; }
    public void setHsCode(String hsCode) { this.hsCode = hsCode; }
    public Double getFobValue() { return fobValue; }
    public void setFobValue(Double fobValue) { this.fobValue = fobValue; }
    public Double getRatePercent() { return ratePercent; }
    public void setRatePercent(Double ratePercent) { this.ratePercent = ratePercent; }
    public Double getIncentiveAmount() { return incentiveAmount; }
    public void setIncentiveAmount(Double incentiveAmount) { this.incentiveAmount = incentiveAmount; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getCompanyId() { return companyId; }
    public void setCompanyId(String companyId) { this.companyId = companyId; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}

package com.exportflow.entity;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import java.util.List;

@Document(collection = "shipments")
public class Shipment {

    @Id
    private String id;
    @Field("shipment_number")
    private String shipmentNumber;
    @Field("buyer_name")
    private String buyerName;
    @Field("buyer_country")
    private String buyerCountry;
    @Field("destination_port")
    private String destinationPort;
    @Field("origin_port")
    private String originPort;
    private String incoterm;
    private String currency;
    @Field("total_value")
    private Double totalValue;
    private String status;
    @Field("expected_ship_date")
    private String expectedShipDate;
    @Field("product_description")
    private String productDescription;
    @Field("hs_codes")
    private List<String> hsCodes;
    @Field("company_id")
    private String companyId;
    @Field("created_by")
    private String createdBy;
    @Field("created_at")
    private String createdAt;
    @Field("updated_at")
    private String updatedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getShipmentNumber() { return shipmentNumber; }
    public void setShipmentNumber(String shipmentNumber) { this.shipmentNumber = shipmentNumber; }
    public String getBuyerName() { return buyerName; }
    public void setBuyerName(String buyerName) { this.buyerName = buyerName; }
    public String getBuyerCountry() { return buyerCountry; }
    public void setBuyerCountry(String buyerCountry) { this.buyerCountry = buyerCountry; }
    public String getDestinationPort() { return destinationPort; }
    public void setDestinationPort(String destinationPort) { this.destinationPort = destinationPort; }
    public String getOriginPort() { return originPort; }
    public void setOriginPort(String originPort) { this.originPort = originPort; }
    public String getIncoterm() { return incoterm; }
    public void setIncoterm(String incoterm) { this.incoterm = incoterm; }
    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }
    public Double getTotalValue() { return totalValue; }
    public void setTotalValue(Double totalValue) { this.totalValue = totalValue; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getExpectedShipDate() { return expectedShipDate; }
    public void setExpectedShipDate(String expectedShipDate) { this.expectedShipDate = expectedShipDate; }
    public String getProductDescription() { return productDescription; }
    public void setProductDescription(String productDescription) { this.productDescription = productDescription; }
    public List<String> getHsCodes() { return hsCodes; }
    public void setHsCodes(List<String> hsCodes) { this.hsCodes = hsCodes; }
    public String getCompanyId() { return companyId; }
    public void setCompanyId(String companyId) { this.companyId = companyId; }
    public String getCreatedBy() { return createdBy; }
    public void setCreatedBy(String createdBy) { this.createdBy = createdBy; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
}

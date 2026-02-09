package com.exportflow.entity;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

@Document(collection = "forex_rates")
public class ForexRate {

    @Id
    private String id;
    private String currency;
    private Double rate;
    private String source;
    @Field("company_id")
    private String companyId;
    private String timestamp;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }
    public Double getRate() { return rate; }
    public void setRate(Double rate) { this.rate = rate; }
    public String getSource() { return source; }
    public void setSource(String source) { this.source = source; }
    public String getCompanyId() { return companyId; }
    public void setCompanyId(String companyId) { this.companyId = companyId; }
    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
}

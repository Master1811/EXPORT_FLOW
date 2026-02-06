package com.exportflow.dto.payment;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PaymentResponse {

    private String id;

    @JsonProperty("shipment_id")
    private String shipmentId;

    private Double amount;
    private String currency;

    @JsonProperty("payment_date")
    private String paymentDate;

    @JsonProperty("payment_mode")
    private String paymentMode;

    @JsonProperty("bank_reference")
    private String bankReference;

    @JsonProperty("exchange_rate")
    private Double exchangeRate;

    @JsonProperty("inr_amount")
    private Double inrAmount;

    private String status;

    @JsonProperty("created_at")
    private String createdAt;
}

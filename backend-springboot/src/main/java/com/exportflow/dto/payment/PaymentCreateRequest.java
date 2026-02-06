package com.exportflow.dto.payment;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class PaymentCreateRequest {

    @NotBlank
    @JsonProperty("shipment_id")
    private String shipmentId;

    @NotNull
    private Double amount;
    private String currency;

    @NotBlank
    @JsonProperty("payment_date")
    private String paymentDate;

    @NotBlank
    @JsonProperty("payment_mode")
    private String paymentMode;

    @JsonProperty("bank_reference")
    private String bankReference;

    @JsonProperty("exchange_rate")
    private Double exchangeRate;

    @JsonProperty("inr_amount")
    private Double inrAmount;
}

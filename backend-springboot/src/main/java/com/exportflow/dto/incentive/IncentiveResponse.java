package com.exportflow.dto.incentive;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IncentiveResponse {

    private String id;

    @JsonProperty("shipment_id")
    private String shipmentId;

    private String scheme;

    @JsonProperty("hs_code")
    private String hsCode;

    @JsonProperty("fob_value")
    private Double fobValue;

    @JsonProperty("rate_percent")
    private Double ratePercent;

    @JsonProperty("incentive_amount")
    private Double incentiveAmount;

    private String status;

    @JsonProperty("created_at")
    private String createdAt;
}

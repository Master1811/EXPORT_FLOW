package com.exportflow.dto.incentive;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

@Data
public class IncentiveCalculateRequest {

    @NotBlank
    @JsonProperty("shipment_id")
    private String shipmentId;

    @NotNull
    @JsonProperty("hs_codes")
    private List<String> hsCodes;

    @NotNull
    @JsonProperty("fob_value")
    private Double fobValue;

    private String currency = "INR";
}

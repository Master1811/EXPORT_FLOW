package com.exportflow.dto.forex;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class ForexRateCreateRequest {

    @NotBlank
    private String currency;

    @NotNull
    private Double rate;

    private String source = "manual";
}

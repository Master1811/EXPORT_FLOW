package com.exportflow.dto.forex;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ForexRateResponse {

    private String id;
    private String currency;
    private Double rate;
    private String source;
    private String timestamp;
}

package com.exportflow.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class AIQueryRequest {

    @NotBlank
    private String query;

    private String context;
}

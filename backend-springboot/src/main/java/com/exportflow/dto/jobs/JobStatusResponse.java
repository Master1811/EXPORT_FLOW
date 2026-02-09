package com.exportflow.dto.jobs;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class JobStatusResponse {

    @JsonProperty("job_id")
    private String jobId;

    private String status;
    private Integer progress;
    private Map<String, Object> result;

    @JsonProperty("created_at")
    private String createdAt;
}

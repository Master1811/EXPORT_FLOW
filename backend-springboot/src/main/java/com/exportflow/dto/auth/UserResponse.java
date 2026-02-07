package com.exportflow.dto.auth;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserResponse {

    private String id;
    private String email;

    @JsonProperty("full_name")
    private String fullName;

    @JsonProperty("company_id")
    private String companyId;

    private String role;

    @JsonProperty("created_at")
    private String createdAt;
}

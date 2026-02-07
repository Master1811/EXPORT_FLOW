package com.exportflow.dto.company;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CompanyResponse {

    private String id;
    private String name;
    private String gstin;
    private String pan;

    @JsonProperty("iec_code")
    private String iecCode;

    private String address;
    private String city;
    private String state;
    private String country;

    @JsonProperty("created_at")
    private String createdAt;
}

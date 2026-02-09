package com.exportflow.dto.company;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class CompanyCreateRequest {

    @NotBlank
    private String name;

    private String gstin;
    private String pan;

    @JsonProperty("iec_code")
    private String iecCode;

    private String address;
    private String city;
    private String state;
    private String country;

    @JsonProperty("bank_account")
    private String bankAccount;

    @JsonProperty("bank_ifsc")
    private String bankIfsc;
}

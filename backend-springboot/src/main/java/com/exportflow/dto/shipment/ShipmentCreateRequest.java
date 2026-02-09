package com.exportflow.dto.shipment;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

@Data
public class ShipmentCreateRequest {

    @NotBlank
    @JsonProperty("shipment_number")
    private String shipmentNumber;

    @NotBlank
    @JsonProperty("buyer_name")
    private String buyerName;

    @NotBlank
    @JsonProperty("buyer_country")
    private String buyerCountry;

    @NotBlank
    @JsonProperty("destination_port")
    private String destinationPort;

    @NotBlank
    @JsonProperty("origin_port")
    private String originPort;

    private String incoterm = "FOB";
    private String currency = "USD";

    @NotNull
    @JsonProperty("total_value")
    private Double totalValue;

    private String status = "draft";

    @JsonProperty("expected_ship_date")
    private String expectedShipDate;

    @JsonProperty("product_description")
    private String productDescription;

    @JsonProperty("hs_codes")
    private List<String> hsCodes;
}

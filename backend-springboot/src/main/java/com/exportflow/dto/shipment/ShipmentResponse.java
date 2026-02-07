package com.exportflow.dto.shipment;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ShipmentResponse {

    private String id;

    @JsonProperty("shipment_number")
    private String shipmentNumber;

    @JsonProperty("buyer_name")
    private String buyerName;

    @JsonProperty("buyer_country")
    private String buyerCountry;

    @JsonProperty("destination_port")
    private String destinationPort;

    @JsonProperty("origin_port")
    private String originPort;

    private String incoterm;
    private String currency;

    @JsonProperty("total_value")
    private Double totalValue;

    private String status;

    @JsonProperty("expected_ship_date")
    private String expectedShipDate;

    @JsonProperty("product_description")
    private String productDescription;

    @JsonProperty("hs_codes")
    private List<String> hsCodes;

    @JsonProperty("company_id")
    private String companyId;

    @JsonProperty("created_at")
    private String createdAt;

    @JsonProperty("updated_at")
    private String updatedAt;
}

package com.exportflow.dto.documents;

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
public class DocumentResponse {

    private String id;

    @JsonProperty("document_type")
    private String documentType;

    @JsonProperty("shipment_id")
    private String shipmentId;

    @JsonProperty("document_number")
    private String documentNumber;

    @JsonProperty("created_at")
    private String createdAt;

    private Map<String, Object> data;
}

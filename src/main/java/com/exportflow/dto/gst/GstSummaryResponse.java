package com.exportflow.dto.gst;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GstSummaryResponse {

    private String month;

    @JsonProperty("total_export_value")
    private Double totalExportValue;

    @JsonProperty("total_igst_paid")
    private Double totalIgstPaid;

    @JsonProperty("refund_eligible")
    private Double refundEligible;

    @JsonProperty("refund_claimed")
    private Double refundClaimed;

    @JsonProperty("refund_pending")
    private Double refundPending;
}

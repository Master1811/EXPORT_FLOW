package com.exportflow.dto.notifications;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class NotificationCreateRequest {

    @NotBlank
    @JsonProperty("user_id")
    private String userId;

    @NotBlank
    private String title;

    @NotBlank
    private String message;

    private String type = "info";
}

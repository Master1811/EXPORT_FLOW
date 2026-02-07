package com.exportflow.controller;

import com.exportflow.dto.notifications.NotificationCreateRequest;
import com.exportflow.security.CurrentUser;
import com.exportflow.service.NotificationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/notifications")
@RequiredArgsConstructor
public class NotificationController {

    private final NotificationService notificationService;

    @PostMapping("/send")
    public Map<String, Object> sendNotification(@Valid @RequestBody NotificationCreateRequest data, @AuthenticationPrincipal CurrentUser user) {
        return notificationService.send(data.getUserId(), data.getTitle(), data.getMessage(), data.getType());
    }

    @GetMapping("/history")
    public List<Map<String, Object>> getNotifications(@AuthenticationPrincipal CurrentUser user) {
        return notificationService.getHistory(user.getId(), 50);
    }
}

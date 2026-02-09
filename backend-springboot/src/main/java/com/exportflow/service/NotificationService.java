package com.exportflow.service;

import com.exportflow.entity.Notification;
import com.exportflow.repository.NotificationRepository;
import com.exportflow.util.IdUtils;
import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class NotificationService {

    private final NotificationRepository notificationRepository;

    @Transactional
    public Map<String, Object> send(String userId, String title, String message, String type) {
        String notifId = IdUtils.generateId();
        Notification n = new Notification();
        n.setId(notifId);
        n.setUserId(userId);
        n.setTitle(title);
        n.setMessage(message);
        n.setType(type != null ? type : "info");
        n.setRead(false);
        n.setCreatedAt(DateTimeUtils.nowIso());
        notificationRepository.save(n);
        return Map.of("id", notifId, "message", "Notification sent");
    }

    public List<Map<String, Object>> getHistory(String userId, int limit) {
        return notificationRepository.findByUserIdOrderByCreatedAtDesc(userId, PageRequest.of(0, limit))
            .stream()
            .map(this::toMap)
            .collect(Collectors.toList());
    }

    private Map<String, Object> toMap(Notification n) {
        return Map.of(
            "id", n.getId(),
            "user_id", n.getUserId(),
            "title", n.getTitle(),
            "message", n.getMessage(),
            "type", n.getType() != null ? n.getType() : "info",
            "read", n.getRead() != null ? n.getRead() : false,
            "created_at", n.getCreatedAt() != null ? n.getCreatedAt() : ""
        );
    }
}

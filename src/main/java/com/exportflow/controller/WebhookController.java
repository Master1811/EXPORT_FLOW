package com.exportflow.controller;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/webhooks")
@RequiredArgsConstructor
public class WebhookController {

    private static final Logger logger = LoggerFactory.getLogger(WebhookController.class);

    @PostMapping("/whatsapp")
    public Map<String, String> whatsappWebhook(@RequestBody Map<String, Object> data) {
        logger.info("WhatsApp webhook received: {}", data);
        return Map.of("status", "received");
    }

    @PostMapping("/bank")
    public Map<String, String> bankWebhook(@RequestBody Map<String, Object> data) {
        logger.info("Bank webhook received: {}", data);
        return Map.of("status", "received");
    }
}

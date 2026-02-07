package com.exportflow.controller;

import com.exportflow.security.CurrentUser;
import com.exportflow.service.ConnectorService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequiredArgsConstructor
public class ConnectorController {

    private final ConnectorService connectorService;

    @PostMapping("/connect/bank/initiate")
    public Map<String, Object> initiateBankConnection(@RequestBody Map<String, Object> data, @AuthenticationPrincipal CurrentUser user) {
        return connectorService.initiateBank(data, user);
    }

    @PostMapping("/connect/bank/consent")
    public Map<String, Object> bankConsent(@RequestBody Map<String, Object> data, @AuthenticationPrincipal CurrentUser user) {
        return connectorService.bankConsent(data, user);
    }

    @GetMapping("/sync/bank")
    public Map<String, Object> syncBankData(@AuthenticationPrincipal CurrentUser user) {
        return connectorService.syncBank(user);
    }

    @PostMapping("/connect/gst/link")
    public Map<String, Object> linkGst(@RequestBody Map<String, Object> data, @AuthenticationPrincipal CurrentUser user) {
        return connectorService.linkGst(data, user);
    }

    @GetMapping("/sync/gst")
    public Map<String, Object> syncGstData(@AuthenticationPrincipal CurrentUser user) {
        return connectorService.syncGst(user);
    }

    @PostMapping("/connect/customs/link")
    public Map<String, Object> linkCustoms(@RequestBody Map<String, Object> data, @AuthenticationPrincipal CurrentUser user) {
        return connectorService.linkCustoms(data, user);
    }

    @GetMapping("/sync/customs")
    public Map<String, Object> syncCustomsData(@AuthenticationPrincipal CurrentUser user) {
        return connectorService.syncCustoms(user);
    }
}

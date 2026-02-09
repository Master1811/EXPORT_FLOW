package com.exportflow.controller;

import com.exportflow.dto.auth.*;
import com.exportflow.security.CurrentUser;
import com.exportflow.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/register")
    public TokenResponse register(@Valid @RequestBody UserCreateRequest data) {
        return authService.register(data);
    }

    @PostMapping("/login")
    public TokenResponse login(@Valid @RequestBody UserLoginRequest data) {
        return authService.login(data);
    }

    @GetMapping("/me")
    public UserResponse getMe(@AuthenticationPrincipal CurrentUser user) {
        return authService.getMe(user);
    }

    @PostMapping("/refresh")
    public TokenResponse refresh(@AuthenticationPrincipal CurrentUser user) {
        return authService.refresh(user);
    }
}

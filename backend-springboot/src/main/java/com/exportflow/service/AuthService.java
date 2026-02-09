package com.exportflow.service;

import com.exportflow.dto.auth.*;
import com.exportflow.entity.Company;
import com.exportflow.entity.User;
import com.exportflow.exception.BadRequestException;
import com.exportflow.exception.UnauthorizedException;
import com.exportflow.repository.CompanyRepository;
import com.exportflow.repository.UserRepository;
import com.exportflow.security.CurrentUser;
import com.exportflow.security.JwtUtil;
import com.exportflow.util.IdUtils;
import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final CompanyRepository companyRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    @Transactional
    public TokenResponse register(UserCreateRequest data) {
        if (userRepository.findByEmail(data.getEmail()).isPresent()) {
            throw new BadRequestException("Email already registered");
        }
        String userId = IdUtils.generateId();
        String companyId = null;
        if (data.getCompanyName() != null && !data.getCompanyName().isBlank()) {
            companyId = IdUtils.generateId();
            Company company = new Company();
            company.setId(companyId);
            company.setName(data.getCompanyName());
            company.setCreatedAt(DateTimeUtils.nowIso());
            companyRepository.save(company);
        }
        User user = new User();
        user.setId(userId);
        user.setEmail(data.getEmail());
        user.setPassword(passwordEncoder.encode(data.getPassword()));
        user.setFullName(data.getFullName());
        user.setCompanyId(companyId);
        user.setRole(companyId != null ? "admin" : "user");
        user.setCreatedAt(DateTimeUtils.nowIso());
        userRepository.save(user);

        String token = jwtUtil.createToken(userId, data.getEmail());
        UserResponse userResponse = toUserResponse(user);
        return TokenResponse.builder()
            .accessToken(token)
            .tokenType("bearer")
            .user(userResponse)
            .build();
    }

    public TokenResponse login(UserLoginRequest data) {
        User user = userRepository.findByEmail(data.getEmail())
            .orElseThrow(() -> new UnauthorizedException("Invalid credentials"));
        if (!passwordEncoder.matches(data.getPassword(), user.getPassword())) {
            throw new UnauthorizedException("Invalid credentials");
        }
        String token = jwtUtil.createToken(user.getId(), user.getEmail());
        UserResponse userResponse = toUserResponse(user);
        return TokenResponse.builder()
            .accessToken(token)
            .tokenType("bearer")
            .user(userResponse)
            .build();
    }

    public UserResponse getMe(CurrentUser currentUser) {
        return UserResponse.builder()
            .id(currentUser.getId())
            .email(currentUser.getEmail())
            .fullName(currentUser.getFullName())
            .companyId(currentUser.getCompanyId())
            .role(currentUser.getRole())
            .createdAt(currentUser.getCreatedAt())
            .build();
    }

    public TokenResponse refresh(CurrentUser currentUser) {
        String token = jwtUtil.createToken(currentUser.getId(), currentUser.getEmail());
        UserResponse userResponse = UserResponse.builder()
            .id(currentUser.getId())
            .email(currentUser.getEmail())
            .fullName(currentUser.getFullName())
            .companyId(currentUser.getCompanyId())
            .role(currentUser.getRole())
            .createdAt(currentUser.getCreatedAt())
            .build();
        return TokenResponse.builder()
            .accessToken(token)
            .tokenType("bearer")
            .user(userResponse)
            .build();
    }

    private UserResponse toUserResponse(User user) {
        return UserResponse.builder()
            .id(user.getId())
            .email(user.getEmail())
            .fullName(user.getFullName())
            .companyId(user.getCompanyId())
            .role(user.getRole() != null ? user.getRole() : "user")
            .createdAt(user.getCreatedAt())
            .build();
    }
}

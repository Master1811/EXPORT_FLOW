package com.exportflow.security;

import com.exportflow.entity.User;
import lombok.Getter;
import org.springframework.security.core.AuthenticatedPrincipal;

import java.util.Map;

@Getter
public class CurrentUser implements AuthenticatedPrincipal {

    private final String id;
    private final String email;
    private final String fullName;
    private final String companyId;
    private final String role;
    private final String createdAt;

    public CurrentUser(String id, String email, String fullName, String companyId, String role, String createdAt) {
        this.id = id;
        this.email = email;
        this.fullName = fullName;
        this.companyId = companyId;
        this.role = role != null ? role : "user";
        this.createdAt = createdAt;
    }

    public static CurrentUser from(User user) {
        return new CurrentUser(
            user.getId(),
            user.getEmail(),
            user.getFullName(),
            user.getCompanyId(),
            user.getRole(),
            user.getCreatedAt()
        );
    }

    public Map<String, Object> toMap() {
        return Map.of(
            "id", id,
            "email", email,
            "full_name", fullName,
            "company_id", companyId != null ? companyId : "",
            "role", role,
            "created_at", createdAt
        );
    }

    @Override
    public String getName() {
        return id;
    }
}

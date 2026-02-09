package com.exportflow.config;

import com.exportflow.security.JwtAuthenticationFilter;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.util.matcher.RequestMatcher;

import jakarta.servlet.http.HttpServletRequest;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Stream;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    // Match paths with or without context path (/api) for permitAll
    private static final List<String> PUBLIC_PATH_PATTERNS = Arrays.asList(
        "/auth/login", "/auth/register", "/health", "/metrics", "/", "/forex/latest", "/webhooks/**",
        "/api/auth/login", "/api/auth/register", "/api/health", "/api/metrics", "/api", "/api/", "/api/forex/latest", "/api/webhooks/**"
    );

    private static boolean isPublicPath(String path) {
        if (path == null) return false;
        String p = path.endsWith("/") && path.length() > 1 ? path.substring(0, path.length() - 1) : path;
        if (p.isEmpty()) p = "/";
        for (String pattern : PUBLIC_PATH_PATTERNS) {
            if (pattern.equals("/") && (p.equals("/") || p.equals("/api"))) return true;
            if (pattern.endsWith("/**")) {
                String prefix = pattern.substring(0, pattern.length() - 3);
                if (p.equals(prefix) || p.startsWith(prefix + "/")) return true;
            } else if (p.equals(pattern)) return true;
        }
        return false;
    }

    private static final RequestMatcher PUBLIC_MATCHER = (HttpServletRequest request) -> {
        String uri = request.getRequestURI();
        String servletPath = request.getServletPath();
        return isPublicPath(uri) || isPublicPath(servletPath);
    };

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(PUBLIC_MATCHER).permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}

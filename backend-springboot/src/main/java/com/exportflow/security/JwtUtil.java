package com.exportflow.security;

import com.exportflow.config.AppProperties;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Date;

@Component
public class JwtUtil {

    private static final int MIN_KEY_BYTES = 32; // 256 bits required for HS256

    private final AppProperties appProperties;
    private final SecretKey key;

    public JwtUtil(AppProperties appProperties) {
        this.appProperties = appProperties;
        byte[] keyBytes = appProperties.getJwt().getSecretKey().getBytes(StandardCharsets.UTF_8);
        if (keyBytes.length < MIN_KEY_BYTES) {
            keyBytes = sha256(keyBytes);
        }
        this.key = Keys.hmacShaKeyFor(keyBytes);
    }

    private static byte[] sha256(byte[] input) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            return digest.digest(input);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 not available", e);
        }
    }

    public String createToken(String userId, String email) {
        long expireMs = appProperties.getJwt().getExpireMinutes() * 60L * 1000L;
        return Jwts.builder()
            .subject(userId)
            .claim("email", email)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + expireMs))
            .signWith(key)
            .compact();
    }

    public Claims decodeToken(String token) {
        return Jwts.parser()
            .verifyWith(key)
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }

    public String getUserIdFromToken(String token) {
        return decodeToken(token).getSubject();
    }

    public boolean isTokenExpired(String token) {
        try {
            decodeToken(token);
            return false;
        } catch (ExpiredJwtException e) {
            return true;
        }
    }
}

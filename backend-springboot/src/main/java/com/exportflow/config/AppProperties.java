package com.exportflow.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "app")
public class AppProperties {

    private Jwt jwt = new Jwt();
    private Cors cors = new Cors();
    private Ai ai = new Ai();

    public Jwt getJwt() { return jwt; }
    public void setJwt(Jwt jwt) { this.jwt = jwt; }
    public Cors getCors() { return cors; }
    public void setCors(Cors cors) { this.cors = cors; }
    public Ai getAi() { return ai; }
    public void setAi(Ai ai) { this.ai = ai; }

    public static class Jwt {
        private String secretKey = "default-secret-key";
        private String algorithm = "HS256";
        private int expireMinutes = 1440;
        public String getSecretKey() { return secretKey; }
        public void setSecretKey(String secretKey) { this.secretKey = secretKey; }
        public String getAlgorithm() { return algorithm; }
        public void setAlgorithm(String algorithm) { this.algorithm = algorithm; }
        public int getExpireMinutes() { return expireMinutes; }
        public void setExpireMinutes(int expireMinutes) { this.expireMinutes = expireMinutes; }
    }

    public static class Cors {
        private String allowedOrigins = "*";
        public String getAllowedOrigins() { return allowedOrigins; }
        public void setAllowedOrigins(String allowedOrigins) { this.allowedOrigins = allowedOrigins; }
    }

    public static class Ai {
        private String emergentLlmKey = "";
        public String getEmergentLlmKey() { return emergentLlmKey; }
        public void setEmergentLlmKey(String emergentLlmKey) { this.emergentLlmKey = emergentLlmKey; }
    }
}

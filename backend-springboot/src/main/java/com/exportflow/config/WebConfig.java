package com.exportflow.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    private final AppProperties appProperties;

    public WebConfig(AppProperties appProperties) {
        this.appProperties = appProperties;
    }

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        String origins = appProperties.getCors().getAllowedOrigins();
        String[] originArray = origins == null || origins.isBlank() ? new String[0] : origins.split("\\s*,\\s*");
        var mapping = registry.addMapping("/**")
            .allowedMethods("*")
            .allowedHeaders("*")
            .allowCredentials(true);
        if (originArray.length == 0 || (originArray.length == 1 && "*".equals(originArray[0].trim()))) {
            mapping.allowedOriginPatterns("*");
        } else {
            mapping.allowedOrigins(originArray);
        }
    }
}

package com.exportflow;

import com.exportflow.config.AppProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties(AppProperties.class)
public class ExportFlowApplication {

    public static void main(String[] args) {
        SpringApplication.run(ExportFlowApplication.class, args);
    }
}

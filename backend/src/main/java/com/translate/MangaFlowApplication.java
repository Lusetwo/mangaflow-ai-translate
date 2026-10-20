package com.translate;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
@ConfigurationPropertiesScan(basePackages = "com.translate.config")
public class MangaFlowApplication {
    public static void main(String[] args) {
        SpringApplication.run(MangaFlowApplication.class,args);
    }
}

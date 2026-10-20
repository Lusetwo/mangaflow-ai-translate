package com.translate.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.ThreadPoolExecutor;

/**
 * 翻译任务异步执行线程池。
 * 供 @Async("translationExecutor") 使用；队列满时由调用线程同步执行，避免任务静默丢失。
 */
@Configuration
public class AsyncConfig {

    @Bean("translationExecutor")
    public ThreadPoolTaskExecutor translationExecutor(
            @Value("${mangaflow.async.executor.core-pool-size:4}") int corePoolSize,
            @Value("${mangaflow.async.executor.max-pool-size:8}") int maxPoolSize,
            @Value("${mangaflow.async.executor.queue-capacity:100}") int queueCapacity,
            @Value("${mangaflow.async.executor.keep-alive-seconds:60}") int keepAliveSeconds,
            @Value("${mangaflow.async.executor.thread-name-prefix:mangaflow-task-}") String threadNamePrefix) {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(corePoolSize);
        executor.setMaxPoolSize(maxPoolSize);
        executor.setQueueCapacity(queueCapacity);
        executor.setKeepAliveSeconds(keepAliveSeconds);
        executor.setThreadNamePrefix(threadNamePrefix);
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(30);
        executor.initialize();
        return executor;
    }
}

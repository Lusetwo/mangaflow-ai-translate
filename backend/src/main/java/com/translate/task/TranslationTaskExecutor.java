package com.translate.task;


import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

@Component
public class TranslationTaskExecutor {
    private final TranslationPipeline pipeline;

    public TranslationTaskExecutor(TranslationPipeline p){
        pipeline = p;
    }

    @Async("translationExecutor")
    public void execute(Long taskId){
        pipeline.execute(taskId);
    }
}

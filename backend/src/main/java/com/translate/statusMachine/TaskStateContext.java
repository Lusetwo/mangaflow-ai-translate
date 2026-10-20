package com.translate.statusMachine;

import com.translate.enums.TaskStage;
import lombok.Builder;

@Builder
public class TaskStateContext {
    private Long taskId;
    private TaskStage currentStage;
    private TaskStage targetStage;
    private String errorMessage;
    private Integer retryCount;
    private Integer progress;
    private String resultPath;

    public Long getTaskId() {
        return taskId;
    }

    public void setTaskId(Long taskId) {
        this.taskId = taskId;
    }

    public TaskStage getCurrentStage() {
        return currentStage;
    }

    public void setCurrentStage(TaskStage currentStage) {
        this.currentStage = currentStage;
    }

    public TaskStage getTargetStage() {
        return targetStage;
    }

    public void setTargetStage(TaskStage targetStage) {
        this.targetStage = targetStage;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public Integer getRetryCount() {
        return retryCount;
    }

    public void setRetryCount(Integer retryCount) {
        this.retryCount = retryCount;
    }

    public Integer getProgress() {
        return progress;
    }

    public void setProgress(Integer progress) {
        this.progress = progress;
    }

    public String getResultPath() {
        return resultPath;
    }

    public void setResultPath(String resultPath) {
        this.resultPath = resultPath;
    }
}

package com.translate.vo;

import com.translate.enums.TaskStage;
import com.translate.enums.TaskStatus;

import java.time.LocalDateTime;

public class TranslationTaskVO {

    private Long taskId;
    private String taskNo;
    private TaskStatus status;
    private TaskStage stage;
    private Integer progress;
    private String sourceLang;
    private String targetLang;
    private boolean resultAvailable;
    private String errorMessage;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public Long getTaskId() {
        return taskId;
    }

    public void setTaskId(Long v) {
        taskId = v;
    }

    public String getTaskNo() {
        return taskNo;
    }

    public void setTaskNo(String v) {
        taskNo = v;
    }

    public TaskStatus getStatus() {
        return status;
    }

    public void setStatus(TaskStatus v) {
        status = v;
    }

    public TaskStage getStage() {
        return stage;
    }

    public void setStage(TaskStage v) {
        stage = v;
    }

    public Integer getProgress() {
        return progress;
    }

    public void setProgress(Integer v) {
        progress = v;
    }

    public String getSourceLang() {
        return sourceLang;
    }

    public void setSourceLang(String v) {
        sourceLang = v;
    }

    public String getTargetLang() {
        return targetLang;
    }

    public void setTargetLang(String v) {
        targetLang = v;
    }

    public boolean isResultAvailable() {
        return resultAvailable;
    }

    public void setResultAvailable(boolean v) {
        resultAvailable = v;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String v) {
        errorMessage = v;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime v) {
        createdAt = v;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime v) {
        updatedAt = v;
    }
}

package com.translate.entity;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.translate.enums.TaskStage;
import com.translate.enums.TaskStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.time.LocalDateTime;

@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("tb_translation_task")
public class TranslationTask implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 主键ID (bigint -> Long)
     */
    @TableId(value = "id")
    private Long id;

    /**
     * 任务编号 (varchar(64) -> String)
     */
    @TableField("task_no")
    private String taskNo;

    /**
     * 状态 (varchar(32) -> String)
     */
    @TableField("status")
    private TaskStatus status;

    /**
     * 阶段 (varchar(32) -> String)
     */
    @TableField("stage")
    private TaskStage stage;

    /**
     * 源语言 (varchar(16) -> String)
     */
    @TableField("source_lang")
    private String sourceLang;

    /**
     * 目标语言 (varchar(16) -> String)
     */
    @TableField("target_lang")
    private String targetLang;

    /**
     * 原始文件路径 (varchar(512) -> String)
     */
    @TableField("original_path")
    private String originalPath;

    /**
     * 结果文件路径 (varchar(512) -> String)
     */
    @TableField("result_path")
    private String resultPath;

    /**
     * 进度 (smallint -> Integer)
     */
    @TableField("progress")
    private Integer progress;

    /**
     * 错误信息 (text -> String)
     */
    @TableField("error_message")
    private String errorMessage;

    /**
     * 重试次数 (integer -> Integer)
     */
    @TableField("retry_count")
    private Integer retryCount;

    /**
     * 创建时间 (timestamp without time zone -> LocalDateTime)
     */
    @TableField(value = "created_at", fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    /**
     * 更新时间 (timestamp without time zone -> LocalDateTime)
     */
    @TableField(value = "updated_at", fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTaskNo() {
        return taskNo;
    }

    public void setTaskNo(String taskNo) {
        this.taskNo = taskNo;
    }

    public TaskStatus getStatus() {
        return status;
    }

    public void setStatus(TaskStatus status) {
        this.status = status;
    }

    public TaskStage getStage() {
        return stage;
    }

    public void setStage(TaskStage stage) {
        this.stage = stage;
    }

    public String getSourceLang() {
        return sourceLang;
    }

    public void setSourceLang(String sourceLang) {
        this.sourceLang = sourceLang;
    }

    public String getTargetLang() {
        return targetLang;
    }

    public void setTargetLang(String targetLang) {
        this.targetLang = targetLang;
    }

    public String getOriginalPath() {
        return originalPath;
    }

    public void setOriginalPath(String originalPath) {
        this.originalPath = originalPath;
    }

    public String getResultPath() {
        return resultPath;
    }

    public void setResultPath(String resultPath) {
        this.resultPath = resultPath;
    }

    public Integer getProgress() {
        return progress;
    }

    public void setProgress(Integer progress) {
        this.progress = progress;
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

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    @Override
    public String toString() {
        return "TranslationTask{" +
                "id=" + id +
                ", taskNo='" + taskNo + '\'' +
                ", status='" + status + '\'' +
                ", stage='" + stage + '\'' +
                ", sourceLang='" + sourceLang + '\'' +
                ", targetLang='" + targetLang + '\'' +
                ", originalPath='" + originalPath + '\'' +
                ", resultPath='" + resultPath + '\'' +
                ", progress=" + progress +
                ", errorMessage='" + errorMessage + '\'' +
                ", retryCount=" + retryCount +
                ", createdAt=" + createdAt +
                ", updatedAt=" + updatedAt +
                '}';
    }
}

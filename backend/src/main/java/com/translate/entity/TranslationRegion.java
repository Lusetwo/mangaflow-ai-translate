package com.translate.entity;


import com.baomidou.mybatisplus.annotation.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.time.LocalDateTime;

@TableName("tb_translation_region")
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TranslationRegion implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 主键id
     */
    @TableId(value = "id")
    private Integer id;

    /***
     * 任务id
     */
    @TableField("task_id")
    private Integer taskId;

    /**
     * 区域编号
     */
    @TableField("region_no")
    private Integer regionNo;

    /**
     * x坐标
     */
    @TableField("x")
    private Integer x;

    /**
     * y坐标
     */
    @TableField("y")
    private Integer y;

    /**
     * 宽度
     */
    @TableField("width")
    private Integer width;

    @TableField("height")
    private Integer height;

    /**
     * 原文
     */
    @TableField("original_text")
    private String originalText;

    /**
     * 译文
     */
    @TableField("translated_text")
    private String translatedText;

    /**
     * 状态：PENDING / PROCESSING / SUCCESS / FAILED 等
     */
    @TableField("status")
    private String status;

    /**
     * 创建时间
     */
    @TableField(value = "created_at", fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    /**
     * 更新时间
     */
    @TableField(value = "updated_at", fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getTaskId() {
        return taskId;
    }

    public void setTaskId(Integer taskId) {
        this.taskId = taskId;
    }

    public Integer getRegionNo() {
        return regionNo;
    }

    public void setRegionNo(Integer regionNo) {
        this.regionNo = regionNo;
    }

    public Integer getX() {
        return x;
    }

    public void setX(Integer x) {
        this.x = x;
    }

    public Integer getY() {
        return y;
    }

    public void setY(Integer y) {
        this.y = y;
    }

    public Integer getWidth() {
        return width;
    }

    public void setWidth(Integer width) {
        this.width = width;
    }

    public Integer getHeight() {
        return height;
    }

    public void setHeight(Integer height) {
        this.height = height;
    }

    public String getOriginalText() {
        return originalText;
    }

    public void setOriginalText(String originalText) {
        this.originalText = originalText;
    }

    public String getTranslatedText() {
        return translatedText;
    }

    public void setTranslatedText(String translatedText) {
        this.translatedText = translatedText;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
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
        return "TranslationRegion{" +
                "id=" + id +
                ", taskId=" + taskId +
                ", regionNo=" + regionNo +
                ", x=" + x +
                ", y=" + y +
                ", width=" + width +
                ", height=" + height +
                ", originalText='" + originalText + '\'' +
                ", translatedText='" + translatedText + '\'' +
                ", status='" + status + '\'' +
                ", createdAt=" + createdAt +
                ", updatedAt=" + updatedAt +
                '}';
    }
}

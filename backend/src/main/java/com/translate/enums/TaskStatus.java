package com.translate.enums;


import lombok.Getter;

import java.util.Arrays;
import java.util.List;

@Getter
public enum TaskStatus {
    PENDING("待处理"),
    PROCESSING("处理中"),
    SUCCESS("成功"),
    FAILED("失败"),
    MANUAL_REQUIRED("需人工干预"); // 用于 OCR 识别失败或需要人工修改译文的场景

    private final String desc;

    TaskStatus(String desc) {
        this.desc = desc;
    }

    /**
     * 定义状态流转规则（核心逻辑）
     * PENDING -> PROCESSING
     * PROCESSING -> SUCCESS / FAILED / MANUAL_REQUIRED
     * FAILED -> PROCESSING (允许重试)
     * MANUAL_REQUIRED -> PROCESSING (人工修改后重新渲染)
     */
    public boolean canTransitionTo(TaskStatus target) {
        return switch (this) {
            case PENDING -> target == PROCESSING;
            case PROCESSING -> target == SUCCESS || target == FAILED || target == MANUAL_REQUIRED;
            case FAILED, MANUAL_REQUIRED -> target == PROCESSING; // 允许重试
            case SUCCESS -> false; // 终态，不允许再流转
        };
    }
}
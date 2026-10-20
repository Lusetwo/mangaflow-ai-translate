package com.translate.enums;

import lombok.Getter;

@Getter
public enum TaskStage {
    QUEUED("已排队"),
    VALIDATING("校验中"),
    OCR_PROCESSING("OCR识别中"),
    TRANSLATING("翻译中"),
    IMAGE_RENDERING("译图渲染中"),
    COMPLETED("已完成"),
    FAILED("已失败");

    private final String desc;

    TaskStage(String desc) {
        this.desc = desc;
    }

    /**
     * 核心：定义合法流转规则
     */
    public boolean canTransitionTo(TaskStage target) {
        // 任何非终态都可以流转到 FAILED
        if (target == FAILED) {
            return this != COMPLETED && this != FAILED;
        }

        return switch (this) {
            case QUEUED -> target == VALIDATING;
            case VALIDATING -> target == OCR_PROCESSING;
            case OCR_PROCESSING -> target == TRANSLATING;
            case TRANSLATING -> target == IMAGE_RENDERING;
            case IMAGE_RENDERING -> target == COMPLETED;
            case FAILED -> target == QUEUED; // 允许重试
            case COMPLETED -> false; // 终态，禁止流转
        };
    }
}
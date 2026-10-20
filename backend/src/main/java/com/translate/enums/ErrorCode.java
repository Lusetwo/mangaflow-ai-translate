package com.translate.enums;

import lombok.Getter;

/**
 * 统一错误码
 * 规则：4xxxx 客户端错误；5xxxx 服务端错误
 */
@Getter
public enum ErrorCode {

    /* ---------- 通用 ---------- */
    SUCCESS(0, "success"),
    BAD_REQUEST(40000, "请求参数错误"),
    UNAUTHORIZED(40100, "未认证"),
    FORBIDDEN(40300, "无权限"),
    NOT_FOUND(40400, "资源不存在"),
    METHOD_NOT_ALLOWED(40500, "请求方法不支持"),
    CONFLICT(40900, "资源冲突"),

    /* ---------- 业务：翻译任务 ---------- */
    TASK_NOT_FOUND(41001, "翻译任务不存在"),
    TASK_STATUS_ILLEGAL(41002, "任务状态不允许该操作"),
    TASK_ALREADY_RUNNING(41003, "任务已在处理中"),
    TASK_NO_DUPLICATE(41004, "任务编号已存在"),
    TASK_RETRY_EXCEEDED(41005, "任务重试次数已达上限"),

    /* ---------- 业务：翻译区域 ---------- */
    REGION_NOT_FOUND(42001, "翻译区域不存在"),
    REGION_NO_DUPLICATE(42002, "同一任务下区域序号重复"),

    /* ---------- 外部依赖 ---------- */
    OCR_SERVICE_ERROR(43001, "OCR 服务调用失败"),
    TRANSLATE_SERVICE_ERROR(43002, "翻译服务调用失败"),
    FILE_UPLOAD_ERROR(43003, "文件上传失败"),

    /* ---------- 服务端 ---------- */
    INTERNAL_ERROR(50000, "服务器内部错误"),
    DATABASE_ERROR(50001, "数据库操作失败");

    private final int code;
    private final String message;

    ErrorCode(int code, String message) {
        this.code = code;
        this.message = message;
    }
}
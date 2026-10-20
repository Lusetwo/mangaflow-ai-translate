package com.translate.exception;

import com.translate.enums.ErrorCode;
import lombok.Getter;

/**
 * 业务异常
 * 用于业务规则校验失败时抛出，会被 GlobalExceptionHandler 捕获并返回统一格式。
 */
@Getter
public class BusinessException extends RuntimeException {

    /** 业务错误码 */
    private final int code;

    /** 是否携带额外数据（可选） */
    private final transient Object data;

    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.code = errorCode.getCode();
        this.data = null;
    }

    public BusinessException(ErrorCode errorCode, Object data) {
        super(errorCode.getMessage());
        this.code = errorCode.getCode();
        this.data = data;
    }

    public BusinessException(ErrorCode errorCode, String message) {
        super(message);
        this.code = errorCode.getCode();
        this.data = null;
    }

    public BusinessException(ErrorCode errorCode, String message, Throwable cause) {
        super(message, cause);
        this.code = errorCode.getCode();
        this.data = null;
    }

    public BusinessException(int code, String message) {
        super(message);
        this.code = code;
        this.data = null;
    }

    /** 常用快捷方法 */
    public static BusinessException of(ErrorCode errorCode) {
        return new BusinessException(errorCode);
    }

    public static BusinessException of(ErrorCode errorCode, String message) {
        return new BusinessException(errorCode, message);
    }

    /** 判断是否为业务异常 */
    public static boolean isBusinessException(Throwable e) {
        return e instanceof BusinessException;
    }
}
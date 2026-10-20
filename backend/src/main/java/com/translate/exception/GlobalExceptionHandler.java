package com.translate.exception;

import com.translate.vo.ApiResponse;
import com.translate.enums.ErrorCode;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ConstraintViolationException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.NoHandlerFoundException;

import java.util.stream.Collectors;

/**
 * 全局异常处理器
 * 统一捕获 Controller 层抛出的异常，返回 ApiResponse 格式。
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /* ======================= 业务异常 ======================= */

    /**
     * 业务异常（最常用）
     */
    @ExceptionHandler(BusinessException.class)
    @ResponseStatus(HttpStatus.OK)
    public ApiResponse<Object> handleBusinessException(BusinessException e, HttpServletRequest request) {
        log.warn("[业务异常] uri={}, code={}, msg={}", request.getRequestURI(), e.getCode(), e.getMessage());
        return new ApiResponse<>(e.getCode(), e.getMessage(), e.getData());
    }

    /* ======================= 参数校验异常 ======================= */

    /**
     * @RequestBody 参数校验失败
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleMethodArgumentNotValid(MethodArgumentNotValidException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
                .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
                .collect(Collectors.joining("; "));
        log.warn("[参数校验失败] {}", msg);
        return ApiResponse.fail(ErrorCode.BAD_REQUEST.getCode(), msg);
    }

    /**
     * 表单绑定校验失败
     */
    @ExceptionHandler(BindException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleBindException(BindException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining("; "));
        log.warn("[参数绑定失败] {}", msg);
        return ApiResponse.fail(ErrorCode.BAD_REQUEST.getCode(), msg);
    }

    /**
     * 方法参数级校验（@Validated 在方法上，如 @NotBlank @RequestParam）
     */
    @ExceptionHandler(ConstraintViolationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleConstraintViolation(ConstraintViolationException e) {
        String msg = e.getConstraintViolations().stream()
                .map(ConstraintViolation::getMessage)
                .collect(Collectors.joining("; "));
        log.warn("[约束校验失败] {}", msg);
        return ApiResponse.fail(ErrorCode.BAD_REQUEST.getCode(), msg);
    }

    /**
     * 缺少请求参数
     */
    @ExceptionHandler(MissingServletRequestParameterException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleMissingParam(MissingServletRequestParameterException e) {
        String msg = "缺少请求参数: " + e.getParameterName();
        log.warn(msg);
        return ApiResponse.fail(ErrorCode.BAD_REQUEST.getCode(), msg);
    }

    /**
     * 参数类型不匹配
     */
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleTypeMismatch(MethodArgumentTypeMismatchException e) {
        String msg = "参数类型错误: " + e.getName();
        log.warn(msg);
        return ApiResponse.fail(ErrorCode.BAD_REQUEST.getCode(), msg);
    }

    /**
     * 请求体不可读（JSON 格式错误等）
     */
    @ExceptionHandler(HttpMessageNotReadableException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleNotReadable(HttpMessageNotReadableException e) {
        log.warn("[请求体解析失败] {}", e.getMessage());
        return ApiResponse.fail(ErrorCode.BAD_REQUEST.getCode(), "请求体格式错误");
    }

    /* ======================= HTTP 异常 ======================= */

    /**
     * 请求方法不支持
     */
    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    @ResponseStatus(HttpStatus.METHOD_NOT_ALLOWED)
    public ApiResponse<Void> handleMethodNotSupported(HttpRequestMethodNotSupportedException e) {
        log.warn("[方法不支持] {}", e.getMessage());
        return ApiResponse.fail(ErrorCode.METHOD_NOT_ALLOWED);
    }

    /**
     * 404
     */
    @ExceptionHandler(NoHandlerFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ApiResponse<Void> handleNoHandlerFound(NoHandlerFoundException e) {
        log.warn("[接口不存在] {}", e.getRequestURL());
        return ApiResponse.fail(ErrorCode.NOT_FOUND);
    }

    /* ======================= 数据库异常 ======================= */

    /**
     * 唯一键冲突
     */
    @ExceptionHandler(DuplicateKeyException.class)
    @ResponseStatus(HttpStatus.CONFLICT)
    public ApiResponse<Void> handleDuplicateKey(DuplicateKeyException e) {
        log.warn("[唯一键冲突] {}", e.getMessage());
        return ApiResponse.fail(ErrorCode.CONFLICT.getCode(), "数据已存在，请勿重复提交");
    }

    /* ======================= 兜底异常 ======================= */

    /**
     * 其他未知异常
     */
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiResponse<Void> handleException(Exception e, HttpServletRequest request) {
        log.error("[系统异常] uri={}", request.getRequestURI(), e);
        return ApiResponse.fail(ErrorCode.INTERNAL_ERROR);
    }
}
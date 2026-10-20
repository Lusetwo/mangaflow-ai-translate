package com.translate.client;

import com.translate.enums.ErrorCode;
import com.translate.exception.BusinessException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;


import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

@Component
public class AiServiceClient {
    private final RestClient restClient;

    public AiServiceClient(RestClient.Builder builder,
                           @Value("${mangaflow.ai.base-url:http://localhost:9000}")String baseUrl,
                           @Value("${mangaflow.ai.connect-timeout:5000}")int connectTimeout,
                           @Value("${mangaflow.ai.read-timeout:60000}")int readTimeout){
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(connectTimeout);
        factory.setReadTimeout(readTimeout);
        this.restClient = builder
                .baseUrl(baseUrl)
                .requestFactory(factory)
                .build();
    }

    public AiServiceResponse translate(Path imagePath, String sourceLang, String targetLang) {

        try {
            // 1. 校验参数
            if (imagePath == null || !Files.isRegularFile(imagePath)) {
                throw new BusinessException(ErrorCode.INTERNAL_ERROR, "图片文件不存在");
            }
            if (sourceLang == null || sourceLang.trim().isEmpty() || targetLang == null || targetLang.trim().isEmpty()) {
                throw new BusinessException(ErrorCode.INTERNAL_ERROR, "源语言或目标语言不能为空");
            }
            // 2. 读取图片
            byte[] bytes = Files.readAllBytes(imagePath);
            if (bytes.length == 0) {
                throw new BusinessException(ErrorCode.INTERNAL_ERROR, "图片文件为空");
            }
            String fileName = imagePath.getFileName().toString();
            // 3. 构建 multipart/form-data 请求
            MultipartBodyBuilder body = new MultipartBodyBuilder();
            body.part("file", new ByteArrayResource(bytes) {
                @Override
                public String getFilename() {
                    return fileName;
                }
            }).contentType(MediaType.parseMediaType(detectContentType(fileName)));

            body.part("source_lang", sourceLang);
            body.part("target_lang", targetLang);

            // 4. 调用 Python AI 服务
            AiServiceResponse response = restClient.post()
                    .uri("/api/v1/translate")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body.build())
                    .retrieve()
                    .body(AiServiceResponse.class);

            // 5. 校验返回结果
            if (response == null || response.getResultImageBase64() == null || response.getResultImageBase64().trim().isEmpty()) {
                throw new BusinessException(ErrorCode.OCR_SERVICE_ERROR, "Python AI 服务未返回结果图片");
            }
            return response;
        } catch (BusinessException ex) {
            // 保留业务异常，不重复包装
            throw ex;
        } catch (Exception ex) {

            // 生产环境应通过日志记录 ex 的完整堆栈
            String detail = ex.getMessage();
            if (detail == null || detail.trim().isEmpty()) {
                detail = "未知错误";
            }
            if (detail.length() > 300) {
                detail = detail.substring(0, 300);
            }
            // 不将底层异常详情直接返回给客户端
            throw new BusinessException(ErrorCode.INTERNAL_ERROR, "调用 Python AI 服务失败"+detail);
        }
    }



    private String detectContentType(String name) {
        String lower = name.toLowerCase(Locale.ROOT);

        if (lower.endsWith(".jpg") || lower.endsWith(".jpeg")) {
            return "image/jpeg";
        }
        if (lower.endsWith(".png")) {
            return "image/png";
        }
        if (lower.endsWith(".webp")) {
            return "image/webp";
        }
        if (lower.endsWith(".bmp")) {
            return "image/bmp";
        }

        throw new BusinessException(ErrorCode.INTERNAL_ERROR, "不支持的图片格式");
    }
}

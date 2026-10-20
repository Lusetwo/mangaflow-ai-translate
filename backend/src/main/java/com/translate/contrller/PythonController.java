package com.translate.contrller;

import com.translate.client.AiServiceClient;
import com.translate.client.AiServiceResponse;
import com.translate.enums.ErrorCode;
import com.translate.exception.BusinessException;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

@RestController
@RequestMapping("/api/v1/p")
public class PythonController {

    private final AiServiceClient aiServiceClient;

    public PythonController(AiServiceClient aiServiceClient){
        this.aiServiceClient = aiServiceClient;
    }

    /**
     * 同步翻译图片
     */
    @PostMapping(
            value = "/translate",
            consumes = MediaType.MULTIPART_FORM_DATA_VALUE
    )
    public AiServiceResponse translate(
            @RequestParam("file") MultipartFile file,
            @RequestParam("source_lang") String sourceLang,
            @RequestParam("target_lang") String targetLang) {

        // 1. 校验上传文件
        if (file == null || file.isEmpty()) {
            throw new BusinessException(
                    ErrorCode.FILE_UPLOAD_ERROR,
                    "上传图片不能为空"
            );
        }

        // 2. 保存到临时文件，适配 AiServiceClient 的 Path 参数
        Path tempFile = null;

        try {
            String originalName = file.getOriginalFilename();
            String suffix = ".png";

            if (originalName != null) {
                int dotIndex = originalName.lastIndexOf('.');
                if (dotIndex >= 0) {
                    suffix = originalName.substring(dotIndex);
                }
            }

            tempFile = Files.createTempFile("translate-", suffix);
            file.transferTo(tempFile);

            // 3. 调用 Python AI 服务
            return aiServiceClient.translate(
                    tempFile,
                    sourceLang,
                    targetLang
            );

        } catch (IOException e) {
            throw new BusinessException(
                    ErrorCode.FILE_UPLOAD_ERROR,
                    "读取上传图片失败"
            );
        } finally {
            // 4. 清理临时文件
            if (tempFile != null) {
                try {
                    Files.deleteIfExists(tempFile);
                } catch (IOException ignored) {
                    // 生产环境建议记录日志
                }
            }
        }
    }
}

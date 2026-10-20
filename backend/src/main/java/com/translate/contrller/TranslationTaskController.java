package com.translate.contrller;


import com.translate.dao.TranslationTaskMapper;
import com.translate.enums.ErrorCode;
import com.translate.exception.BusinessException;
import com.translate.service.TranslationRegionService;
import com.translate.service.TranslationTaskService;
import com.translate.vo.ApiResponse;
import com.translate.vo.TranslationTaskVO;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

@RestController
@RequestMapping("/api/v1/tasks")
@Validated
public class TranslationTaskController {
    private final TranslationTaskService translationTaskService;

    private final TranslationTaskMapper translationTaskMapper;

    private final TranslationRegionService translationRegionService;

    public TranslationTaskController(TranslationTaskService s,TranslationTaskMapper m,TranslationRegionService r){
        translationTaskService = s;
        translationTaskMapper = m;
        translationRegionService = r;
    }

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ApiResponse<TranslationTaskVO> create(
            @RequestPart("file") MultipartFile file,
            @RequestParam(defaultValue="ja") @Size(max=16) @Pattern(regexp="^[a-zA-Z-]+$") String sourceLang,
            @RequestParam(defaultValue="zh-CN") @Size(max=16) @Pattern(regexp="^[a-zA-Z-]+$") String targetLang){
        return ApiResponse.success(translationTaskService.createTask(file,sourceLang,targetLang));
    }

    @GetMapping("/{taskId}")
    public ApiResponse<TranslationTaskVO> get(@PathVariable Long taskId){
        TranslationTaskVO translationTaskVO = translationTaskService.getTask(taskId);
        return ApiResponse.success(translationTaskVO);
    }

    @PostMapping("/{taskId}/retry")
    public ApiResponse<Void> retry(@PathVariable Long taskId){
        translationTaskService.retryTask(taskId);
        return ApiResponse.success();
    }


    @GetMapping("/{taskId}/result")
    public ResponseEntity<byte[]> result(@PathVariable Long taskId)throws IOException {
        var task=translationTaskMapper.selectById(taskId);
        if(task==null)throw new BusinessException(ErrorCode.NOT_FOUND,"任务不存在");
        if(task.getResultPath()==null||task.getResultPath().isBlank())throw new BusinessException(ErrorCode.NOT_FOUND,"译图尚未生成");
        Path path=translationRegionService.resolveStoredPath(task.getResultPath());
        if(!Files.exists(path)||!Files.isRegularFile(path))throw new BusinessException(ErrorCode.NOT_FOUND,"译图文件不存在");
        return ResponseEntity.ok().contentType(MediaType.IMAGE_PNG)
                .header(HttpHeaders.CONTENT_DISPOSITION,"attachment; filename=\"translate-result-"+taskId+".png\"")
                .body(Files.readAllBytes(path));
    }

}

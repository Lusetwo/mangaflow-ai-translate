package com.translate.service;

import com.translate.vo.TranslationTaskVO;
import org.springframework.web.multipart.MultipartFile;

public interface TranslationTaskService {
    public TranslationTaskVO createTask(MultipartFile file, String sourceLang, String targetLang);

    public TranslationTaskVO getTask(Long id);

    public void retryTask(Long id);
}

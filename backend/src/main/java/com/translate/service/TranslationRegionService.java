package com.translate.service;


import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Path;

public interface TranslationRegionService {

    Path storeOriginal(MultipartFile file) throws IOException;

    Path createResultPath(String taskNo) throws IOException;

    Path resolveStoredPath(String storedPath);

    String toStoredPath(Path path);

}

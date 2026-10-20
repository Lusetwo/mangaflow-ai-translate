package com.translate.service.impl;

import com.translate.config.StorageProperties;
import com.translate.enums.ErrorCode;
import com.translate.exception.BusinessException;
import com.translate.service.TranslationRegionService;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import javax.imageio.ImageIO;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;

@Service
public class TranslationRegionServiceImpl implements TranslationRegionService {

    //定义图片格式
    private static final Set<String> ALLOWED = Set.of("png","jpeg","jpg");

    private final Path root;

    private final long maxBytes;

    public TranslationRegionServiceImpl(StorageProperties p){
        //获取根目录
        root = Paths.get(p.getRootDir()).toAbsolutePath().normalize();

        //获取根目录存储大小
        maxBytes = p.getMaxFileSizeBytes();

        try{
            Files.createDirectories(root.resolve("original"));
            Files.createDirectories(root.resolve("result"));

        }catch (IOException e){
            throw new IllegalStateException("无法初始化文件存储目录",e);
        }
    }
    @Override
    public Path storeOriginal(MultipartFile file)throws IOException{
        if (file==null||file.isEmpty()) throw new BusinessException(ErrorCode.NOT_FOUND,"上传文件不能为空");
        if (file.getSize()>maxBytes)throw new BusinessException(ErrorCode.FILE_UPLOAD_ERROR,"文件大小超过限制");
        String name = file.getOriginalFilename() == null?"":file.getOriginalFilename();
        int dot = name.lastIndexOf('.');
        String ext = dot<0?"":name.substring(dot+1).toLowerCase(Locale.ROOT);
        if (!ALLOWED.contains(ext))throw new BusinessException(ErrorCode.BAD_REQUEST,"仅支持 PNG,JPG,JPEG图片");
        try(var in=file.getInputStream()) {
            if(ImageIO.read(in)==null)throw new BusinessException(ErrorCode.BAD_REQUEST,"文件不是有效的 PNG/JPEG 图片");
        }
        Path dest=root.resolve("original").resolve(UUID.randomUUID().toString().replace("-","")+"."+ext).normalize();
        if(!dest.startsWith(root))throw new BusinessException(ErrorCode.CONFLICT,"非法文件路径");
        try(var in=file.getInputStream()){
            Files.copy(in,dest);
        }
        return dest;
    }

    @Override
    public Path createResultPath(String taskNo) throws IOException{
        Path dir = root.resolve("result").normalize();
        Files.createDirectories(dir);
        Path p = dir.resolve(taskNo + "-translated.png").normalize();
        if (!p.startsWith(root)) throw  new BusinessException(ErrorCode.CONFLICT,"非法文件路径");
        return p;
    }

    @Override
    public Path resolveStoredPath(String storedPath){
        if (storedPath == null || storedPath.isBlank()) throw new BusinessException(ErrorCode.NOT_FOUND,"文件不存在");
        Path p = Paths.get(storedPath).toAbsolutePath().normalize();
        if (!p.startsWith(root))throw new BusinessException(ErrorCode.CONFLICT,"非法文件路径");
        return p;
    }

    @Override
    public String toStoredPath(Path path){
        Path p = path.toAbsolutePath().normalize();
        if (!p.startsWith(root))throw new BusinessException(ErrorCode.NOT_FOUND,"文件不在存储目录中");
        return p.toString();
    }
}

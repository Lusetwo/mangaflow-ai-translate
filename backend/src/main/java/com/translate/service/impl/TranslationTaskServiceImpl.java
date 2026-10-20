package com.translate.service.impl;

import com.translate.dao.TranslationTaskMapper;
import com.translate.entity.TranslationTask;
import com.translate.enums.ErrorCode;
import com.translate.enums.TaskStage;
import com.translate.enums.TaskStatus;
import com.translate.exception.BusinessException;
import com.translate.service.TranslationRegionService;
import com.translate.service.TranslationTaskService;
import com.translate.statusMachine.TaskStateContext;
import com.translate.statusMachine.TaskStateMachine;
import com.translate.task.TranslationTaskExecutor;
import com.translate.vo.TranslationTaskVO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class TranslationTaskServiceImpl implements TranslationTaskService {

    private final TranslationTaskMapper translationTaskMapper;

    private final TranslationRegionService translationRegionService;

    private final TranslationTaskExecutor executor;

    public TranslationTaskServiceImpl(TranslationTaskMapper m,TranslationRegionService s,TranslationTaskExecutor e){
        translationTaskMapper = m;
        translationRegionService = s;
        executor = e;
    }

    @Autowired
    private  TaskStateMachine stateMachine;

    @Value("${mangaflow.task.max-retry:5}")
    private int maxRetry;

    @Override
    @Transactional
    public TranslationTaskVO createTask(MultipartFile file,String sourceLang,String targetLang){
        if (sourceLang == null || sourceLang.isBlank() || targetLang == null || targetLang.isBlank()){
            throw  new BusinessException(ErrorCode.FILE_UPLOAD_ERROR,"原始语言和目标语言不能为空");
        }

        //任务id
        String no = "MF-" + UUID.randomUUID().toString().replace("-","").substring(0,16).toUpperCase();

        Path original;
        try{
            original = translationRegionService.storeOriginal(file);
        }catch (IOException e){
            throw new BusinessException(ErrorCode.FILE_UPLOAD_ERROR,"保存原始图片失败");
        }
        LocalDateTime now = LocalDateTime.now();
        TranslationTask t = new TranslationTask();

        t.setTaskNo(no);
        t.setStatus(TaskStatus.PENDING);
        t.setStage(TaskStage.QUEUED);
        t.setSourceLang(sourceLang);
        t.setTargetLang(targetLang);
        t.setOriginalPath(translationRegionService.toStoredPath(original));
        t.setProgress(0);
        t.setRetryCount(0);
        t.setCreatedAt(now);
        t.setUpdatedAt(now);

        translationTaskMapper.insert(t);

        // ✅ 事务提交后再触发（用 Spring 事件解耦，或 TransactionSynchronization）
        registerAfterCommit(() -> executor.execute(t.getId()));

        return toVO(t);
    }

    @Override
    @Transactional
    public TranslationTaskVO getTask(Long id){
        TranslationTask t = translationTaskMapper.selectById(id);
        if (t == null) throw new BusinessException(ErrorCode.NOT_FOUND,"任务不存在");
        return toVO(t);
    }

    @Override
    @Transactional
    public void retryTask(Long id){
        TranslationTask t = translationTaskMapper.selectById(id);
        if (t == null) throw new BusinessException(ErrorCode.NOT_FOUND,"任务不存在");
        if (t.getStatus() != TaskStatus.FAILED) throw new BusinessException(ErrorCode.BAD_REQUEST,"只有任务失败允许重试");

        int currentRetry = t.getRetryCount() == null ? 0 : t.getRetryCount();
        if (currentRetry >= maxRetry) {
            throw new BusinessException(ErrorCode.TASK_RETRY_EXCEEDED,"任务重试次数已达上限(" + maxRetry + ")");
        }

        // 通过状态机流转：FAILED -> QUEUED 带乐观锁（状态机是唯一写入口，避免先 updateById 导致乐观锁条件失效）
        boolean fired = stateMachine.fire(TaskStateContext.builder()
                .taskId(id)
                .currentStage(TaskStage.FAILED)
                .targetStage(TaskStage.QUEUED)
                .retryCount(currentRetry + 1)
                .progress(0)
                .errorMessage("") // 置空错误信息
                .build());

        if (!fired) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "任务状态已变更，请刷新后重试");
        }


        registerAfterCommit(() -> executor.execute(id));
    }



    private TranslationTaskVO toVO(TranslationTask t){
        TranslationTaskVO v = new TranslationTaskVO();
        v.setTaskId(t.getId());
        v.setTaskNo(t.getTaskNo());
        v.setStatus(t.getStatus());
        v.setStage(t.getStage());
        v.setProgress(t.getProgress());
        v.setSourceLang(t.getSourceLang());
        v.setTargetLang(t.getTargetLang());
        v.setResultAvailable(t.getResultPath()!=null&&!t.getResultPath().isBlank());
        v.setErrorMessage(t.getErrorMessage());
        v.setCreatedAt(t.getCreatedAt());
        v.setUpdatedAt(t.getUpdatedAt());
        return v;
    }

    private void registerAfterCommit(Runnable action) {
        if (TransactionSynchronizationManager.isSynchronizationActive()) {
            TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
                @Override
                public void afterCommit() {
                    action.run();
                }
            });
        } else {
            action.run(); // 没有事务上下文，直接执行
        }
    }
}

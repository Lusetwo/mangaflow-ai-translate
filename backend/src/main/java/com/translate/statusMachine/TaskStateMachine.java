package com.translate.statusMachine;

import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.translate.dao.TranslationTaskMapper;
import com.translate.entity.TranslationTask;
import com.translate.enums.TaskStage;
import com.translate.enums.TaskStatus;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Slf4j
@Component
@RequiredArgsConstructor
public class TaskStateMachine {

    private final TranslationTaskMapper taskMapper;

    public boolean fire(TaskStateContext context) {
        TaskStage current = context.getCurrentStage();
        TaskStage target = context.getTargetStage();

        // 1. 校验流转合法性
        if (current != null && !current.canTransitionTo(target)) {
            log.warn("任务[{}]非法状态流转: {} -> {}", context.getTaskId(), current, target);
            throw new IllegalStateException("非法状态流转: " + current + " -> " + target);
        }

        // 2. 推导 status 字段的值 (兼容数据库设计)
        TaskStatus derivedStatus = switch (target) {
            case QUEUED -> TaskStatus.PENDING;
            case COMPLETED -> TaskStatus.SUCCESS;
            case FAILED -> TaskStatus.FAILED;
            default -> TaskStatus.PROCESSING; // VALIDATING, OCR_PROCESSING 等
        };

        // 3. 构建乐观锁更新条件 (WHERE id = ? AND stage = ?)
        LambdaUpdateWrapper<TranslationTask> wrapper = new LambdaUpdateWrapper<>();
        wrapper.eq(TranslationTask::getId, context.getTaskId());
        if (current != null) {
            wrapper.eq(TranslationTask::getStage, current.name()); // 防止并发覆盖
        }

        // 4. 构建更新内容
        TranslationTask updateEntity = new TranslationTask();
        updateEntity.setStage(target);
        updateEntity.setStatus(derivedStatus);
        updateEntity.setUpdatedAt(LocalDateTime.now());

        if (context.getErrorMessage() != null) {
            updateEntity.setErrorMessage(context.getErrorMessage());
        }
        if (context.getRetryCount() != null) {
            updateEntity.setRetryCount(context.getRetryCount());
        }
        if (context.getProgress() != null) {
            updateEntity.setProgress(context.getProgress());
        }
        if (context.getResultPath() != null) {
            updateEntity.setResultPath(context.getResultPath());
        }

        // 5. 执行更新
        int rows = taskMapper.update(updateEntity, wrapper);

        if (rows == 0) {
            log.warn("任务[{}]状态流转失败，可能已被其他线程修改。预期阶段: {}", context.getTaskId(), current);
            return false;
        }

        log.info("任务[{}]阶段流转成功: {} -> {}", context.getTaskId(), current, target);
        return true;
    }
}

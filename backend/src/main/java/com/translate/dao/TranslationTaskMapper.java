package com.translate.dao;


import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.translate.entity.TranslationTask;
import com.translate.dto.StatusCountDTO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface TranslationTaskMapper extends BaseMapper<TranslationTask> {

    TranslationTask selectByTaskNo(@Param("taskNo") String taskNo);

    List<TranslationTask> selectPageByStatus(@Param("status") String status);

    List<TranslationTask> fetchPendingTasks(@Param("limit") int limit);

    List<StatusCountDTO> countByStatus();

    List<TranslationTask> selectRetryable(@Param("maxRetry") int maxRetry,
                                          @Param("limit") int limit);

    int updateProgress(@Param("id") Long id,
                       @Param("progress") Integer progress,
                       @Param("stage") String stage);

    int markSuccess(@Param("id") Long id,
                    @Param("resultPath") String resultPath);

    int markFailed(@Param("id") Long id,
                   @Param("errorMessage") String errorMessage);

    int markTimeoutTasks(@Param("minutes") int minutes);
}

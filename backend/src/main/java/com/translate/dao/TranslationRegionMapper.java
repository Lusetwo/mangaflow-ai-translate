package com.translate.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.translate.entity.TranslationRegion;
import com.translate.dto.StatusCountDTO;
import com.translate.dto.TaskRegionDTO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface TranslationRegionMapper extends BaseMapper<TranslationRegion> {

    List<TranslationRegion> selectByTaskId(@Param("taskId") Long taskId);

    List<TranslationRegion> selectPendingByTaskId(@Param("taskId") Long taskId);

    int batchInsert(@Param("list") List<TranslationRegion> list);

    int batchUpdateTranslated(@Param("list") List<TranslationRegion> list);

    List<StatusCountDTO> countByStatus(@Param("taskId") Long taskId);

    List<TaskRegionDTO> selectTaskWithRegions(@Param("taskNo") String taskNo);

    int updateTaskProgressByRegions(@Param("taskId") Long taskId);
}

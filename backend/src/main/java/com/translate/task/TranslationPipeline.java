package com.translate.task;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.translate.client.AiServiceClient;
import com.translate.client.AiServiceResponse;
import com.translate.dao.TranslationRegionMapper;
import com.translate.dao.TranslationTaskMapper;
import com.translate.entity.TranslationRegion;
import com.translate.entity.TranslationTask;
import com.translate.enums.ErrorCode;
import com.translate.enums.TaskStage;
import com.translate.enums.TaskStatus;
import com.translate.exception.BusinessException;
import com.translate.service.TranslationRegionService;
import com.translate.statusMachine.TaskStateContext;
import com.translate.statusMachine.TaskStateMachine;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;

@Component
public class TranslationPipeline {

    private static final int MAX_ERR_LEN = 2000;
    private static final int BOX_MARGIN = 10;
    private static final int BOX_HEIGHT = 42;

    private final TranslationTaskMapper translationTaskMapper;
    private final TranslationRegionService translationRegionService;
    private final TaskStateMachine taskStateMachine;
    private final AiServiceClient aiServiceClient;
    private final TranslationRegionMapper translationRegionMapper;
    //开关：true = 演示流程（不依赖 Python 服务）；false = 真实 AI 翻译
    private final boolean demoEnabled;

    public TranslationPipeline(TranslationTaskMapper m,
                               TranslationRegionService s,
                               @Value("${mangaflow.pipeline.demo-enabled:true}") boolean d,
                               TaskStateMachine machine,
                               AiServiceClient ai,
                               TranslationRegionMapper regionMapper) {
        translationTaskMapper = m;
        translationRegionService = s;
        demoEnabled = d;
        taskStateMachine = machine;
        aiServiceClient = ai;
        translationRegionMapper = regionMapper;
    }

    /***
     * 主流程：
     * 上传图片 → 创建任务(QUEUED) → 异步 execute(id)
     *   ↓
     * ① QUEUED → VALIDATING(5%)：读取并校验原图
     *   ↓
     * ② VALIDATING → OCR_PROCESSING(25%)：调用 Python AI 服务（一次调用完成 OCR + 翻译 + 整图渲染）
     *   ↓
     * ③ OCR_PROCESSING → TRANSLATING(55%)：解析响应，OCR 区域数据落库 tb_translation_region
     *   ↓
     * ④ TRANSLATING → IMAGE_RENDERING(80%)：解码 resultImageBase64，写入译图文件
     *   ↓
     * ⑤ IMAGE_RENDERING → COMPLETED(100%)：result_path 落库
     *
     * demoEnabled=true 时走演示画图分支（作为 Python 服务不可用时的回退）。
     */
    public void execute(Long id) {
        TranslationTask task = translationTaskMapper.selectById(id);

        //任务完成或者不存在
        if (task == null || task.getStatus() == TaskStatus.SUCCESS) return;

        TaskStage currentStage = task.getStage();

        try {
            //校验原图
            if (!fire(task, currentStage, TaskStage.VALIDATING, 5)) return;

            BufferedImage source = ImageIO.read(translationRegionService.resolveStoredPath(task.getOriginalPath()).toFile());
            if (source == null) {
                throw new BusinessException(ErrorCode.CONFLICT, "无法读取原始图片");
            }

            if (demoEnabled) {
                executeDemo(task, source);
            } else {
                executeAi(task);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            markFailed(task, "任务被中断");

        } catch (Exception e) {
            markFailed(task, e.getMessage() == null ? "任务执行失败" : e.getMessage());
        }
    }

    /** 演示流程：画一个 "MangaFlow AI - Demo Result" 白色标签，快速穿过中间阶段保证状态机流转合法 */
    private void executeDemo(TranslationTask task, BufferedImage source) throws Exception {
        if (!fire(task, TaskStage.VALIDATING, TaskStage.OCR_PROCESSING, 25)) return;
        if (!fire(task, TaskStage.OCR_PROCESSING, TaskStage.TRANSLATING, 55)) return;
        if (!fire(task, TaskStage.TRANSLATING, TaskStage.IMAGE_RENDERING, 80)) return;

        Path result = translationRegionService.createResultPath(task.getTaskNo());
        writeDemoResult(source, result);

        fire(task, TaskStage.IMAGE_RENDERING, TaskStage.COMPLETED, 100,
                translationRegionService.toStoredPath(result));
    }

    /** 真实 AI 流程：调用 Python 服务 → regions 落库 → 译图落盘 */
    private void executeAi(TranslationTask task) throws Exception {
        //② 调用 AI 服务（OCR + 翻译 + 渲染在 Python 端一次完成）
        if (!fire(task, TaskStage.VALIDATING, TaskStage.OCR_PROCESSING, 25)) return;

        AiServiceResponse resp = aiServiceClient.translate(
                translationRegionService.resolveStoredPath(task.getOriginalPath()),
                task.getSourceLang(),
                task.getTargetLang());

        //③ 解析响应，OCR 区域数据落库（重试幂等：先清旧数据）
        if (!fire(task, TaskStage.OCR_PROCESSING, TaskStage.TRANSLATING, 55)) return;
        saveRegions(task, resp);

        //④ 解码译图并写文件
        if (!fire(task, TaskStage.TRANSLATING, TaskStage.IMAGE_RENDERING, 80)) return;
        Path result = translationRegionService.createResultPath(task.getTaskNo());
        Files.write(result, decodeResultImage(resp.getResultImageBase64()));

        //⑤ 完成，result_path 落库
        fire(task, TaskStage.IMAGE_RENDERING, TaskStage.COMPLETED, 100,
                translationRegionService.toStoredPath(result));
    }

    /** OCR 区域数据落库：原文/译文/坐标写入 tb_translation_region */
    private void saveRegions(TranslationTask task, AiServiceResponse resp) {
        translationRegionMapper.delete(new LambdaQueryWrapper<TranslationRegion>()
                .eq(TranslationRegion::getTaskId, task.getId().intValue()));

        List<AiServiceResponse.TextRegionResult> regions = resp.getRegions();
        if (regions == null || regions.isEmpty()) return;

        List<String> translations = resp.getTranslations();
        List<TranslationRegion> list = new ArrayList<>(regions.size());
        LocalDateTime now = LocalDateTime.now();
        for (int i = 0; i < regions.size(); i++) {
            AiServiceResponse.TextRegionResult r = regions.get(i);

            String translated = null;
            String status = "OCR_DONE";
            if (translations != null && i < translations.size()
                    && translations.get(i) != null && !translations.get(i).isBlank()) {
                translated = translations.get(i);
                status = "TRANSLATED";
            }

            list.add(TranslationRegion.builder()
                    .taskId(task.getId().intValue())
                    .regionNo(i + 1)
                    .x(r.getX())
                    .y(r.getY())
                    .width(r.getWidth())
                    .height(r.getHeight())
                    .originalText(r.getText())
                    .translatedText(translated)
                    .status(status)
                    .createdAt(now)
                    .updatedAt(now)
                    .build());
        }
        translationRegionMapper.batchInsert(list);
    }

    /** 解码 Python 返回的译图 base64（容忍 data:image/...;base64, 前缀与换行） */
    private byte[] decodeResultImage(String base64) {
        if (base64 == null || base64.isBlank()) {
            throw new BusinessException(ErrorCode.OCR_SERVICE_ERROR, "AI 服务未返回结果图片");
        }
        String payload = base64.trim();
        if (payload.startsWith("data:")) {
            int comma = payload.indexOf(',');
            if (comma >= 0) payload = payload.substring(comma + 1);
        }
        byte[] bytes = Base64.getMimeDecoder().decode(payload);
        if (bytes.length == 0) {
            throw new BusinessException(ErrorCode.OCR_SERVICE_ERROR, "结果图片解码为空");
        }
        return bytes;
    }

    private void writeDemoResult(BufferedImage source, Path path) throws Exception {
        Files.createDirectories(path.getParent());
        BufferedImage out = new BufferedImage(source.getWidth(), source.getHeight(), BufferedImage.TYPE_INT_ARGB);
        Graphics2D g = out.createGraphics();

        try {
            g.drawImage(source, 0, 0, null);
            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            int w = Math.min(source.getWidth() - 20, Math.max(100, source.getWidth() / 2));
            g.setColor(new Color(255, 255, 255, 235));
            g.fillRoundRect(BOX_MARGIN, BOX_MARGIN, Math.max(1, w), BOX_HEIGHT, BOX_MARGIN, BOX_MARGIN);
            g.setColor(Color.DARK_GRAY);
            g.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, Math.max(BOX_MARGIN, Math.min(16, source.getWidth() / 30))));
            g.drawString("MangaFlow AI - Demo Result", 16, 36);
        } finally {
            g.dispose();
        }
        ImageIO.write(out, "png", path.toFile());
    }

    /**
     * 通过状态机推进 返回 false 表示并发抢锁失败
     */
    private boolean fire(TranslationTask task, TaskStage from, TaskStage to, int progress) {
        return fire(task, from, to, progress, null);
    }

    private boolean fire(TranslationTask task, TaskStage from, TaskStage to, int progress, String resultPath) {
        boolean ok = taskStateMachine.fire(TaskStateContext.builder()
                .taskId(task.getId())
                .currentStage(from)
                .targetStage(to)
                .progress(progress)
                .resultPath(resultPath)
                .build());
        if (ok) {
            task.setStage(to);
            task.setProgress(progress);
            if (resultPath != null) {
                task.setResultPath(resultPath);
            }
        }
        return ok;
    }

    private void markFailed(TranslationTask task, String msg) {
        if (msg.length() > MAX_ERR_LEN) {
            msg = msg.substring(0, MAX_ERR_LEN);
        }
        taskStateMachine.fire(TaskStateContext.builder()
                .taskId(task.getId())
                .currentStage(task.getStage())
                .targetStage(TaskStage.FAILED)
                .errorMessage(msg)
                .build());
    }
}

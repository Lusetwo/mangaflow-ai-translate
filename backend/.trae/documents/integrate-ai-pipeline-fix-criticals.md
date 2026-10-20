# 计划：AI 翻译接入异步主流程 + 修复致命缺陷

## 摘要

当前后端主流程（上传建任务 → 异步 pipeline）只跑 demo 画图，已写好的 `AiServiceClient`（调用 Python AI 服务）从未接入。同时存在 5 个致命缺陷：配置前缀不匹配（环境变量全部失效）、`@Async("translationExecutor")` 缺少线程池 Bean、状态机不落库 `progress`/`result_path`（译图下载永远 404）、`TranslationTaskMapper.xml` namespace 错误、数据库无 schema。

本计划：① 修复全部致命缺陷；② 将 AI 服务接入异步主流程（译图直接用 Python 返回的 `resultImageBase64` 落盘，OCR 区域数据存入 `tb_translation_region`）；③ 保留 `demoEnabled` 开关作为回退；④ 顺手修 retry 逻辑 bug 与 AI 客户端超时缺失。

**已确认的决策**：译图产出 = 直接保存 `resultImageBase64`；regions 落库 = 是；Python AI 服务（localhost:8000）已就绪可联调。

## 现状分析（问题清单）

| # | 问题 | 位置 | 影响 |
|---|------|------|------|
| 1 | 配置前缀不匹配 | [StorageProperties.java](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/config/StorageProperties.java) prefix=`storage`（yml 是 `mangaflow.storage`）；[AiServiceClient.java:22](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/client/AiServiceClient.java#L22) 读 `translate.ai.base-url`（实际指向 9000，AI 在 8000）；[TranslationPipeline.java:38](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/task/TranslationPipeline.java#L38) 读 `translate.pipeline.demo-enabled` | `STORAGE_ROOT`/`AI_BASE_URL`/`DEMO_PIPELINE_ENABLED` 环境变量全部失效 |
| 2 | `@Async("translationExecutor")` 无对应 Bean | [TranslationTaskExecutor.java:15](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/task/TranslationTaskExecutor.java#L15)，项目中无 AsyncConfig | 第一次异步调用抛 `NoSuchBeanDefinitionException`，主流程不可用 |
| 3 | progress / result_path 不落库 | [TaskStateMachine.java:46-57](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/statusMachine/TaskStateMachine.java#L46-57) 只更新 stage/status/updatedAt/errorMessage/retryCount；pipeline 里 `setResultPath`/`setProgress` 只改内存 | 任务完成后 DB `result_path=NULL`，`/result` 接口永远 404；前端轮询进度恒为 0 |
| 4 | Mapper XML namespace 错误 | [TranslationTaskMapper.xml:5](file:///d:/project/java_code/mangaflow-ai-translate/src/main/resources/mapper/TranslationTaskMapper.xml#L5) 是 `com.translate.mapper.*`，接口在 `com.translate.dao`（注：RegionMapper.xml 的 namespace 是对的，不用动） | 任务侧 9 个自定义 SQL 绑定失败，调用即报错；L90 `stage='DONE'` 不是合法枚举值 |
| 5 | 无 schema | 全仓库无 schema.sql/data.sql/Flyway；dev 配置 `sql.init.mode: always` 但无脚本 | 表不存在则启动后所有 SQL 失败 |
| 6 | AI 未接入主流程 | [TranslationPipeline.java:75-76](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/task/TranslationPipeline.java#L75-76) demo 关闭时直接抛异常 | 核心功能（翻译）不存在 |
| 7 | AI 客户端无超时 | [AiServiceClient.java:21-24](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/client/AiServiceClient.java#L21-24) 只设 baseUrl；yml 的 connect/read-timeout 未被使用 | AI 处理慢时线程无限挂起 |
| 8 | retryCount 双重 +1；retry 用 fail 语义返回成功 | [TranslationTaskServiceImpl.java:101-110](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/service/impl/TranslationTaskServiceImpl.java#L101-110)、[L57](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/contrller/TranslationTaskController.java#L57) | 重试次数虚增；接口语义混乱 |
| 9 | createTask 误用 NOT_FOUND 错误码 | [TranslationTaskServiceImpl.java:59](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/service/impl/TranslationTaskServiceImpl.java#L59) | 错误码语义错误 |

## 变更清单

### 1. 配置前缀修复（问题 1、9）

- **[StorageProperties.java](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/config/StorageProperties.java)**：`@ConfigurationProperties(prefix = "storage")` → `prefix = "mangaflow.storage"`
- **[AiServiceClient.java](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/client/AiServiceClient.java)**：`@Value` 改为 `${mangaflow.ai.base-url:http://localhost:8000}`；同时新增 `connect-timeout`/`read-timeout` 两个 `@Value`（`mangaflow.ai.connect-timeout` / `mangaflow.ai.read-timeout`），用 `SimpleClientHttpRequestFactory` 设置超时后传入 `RestClient.Builder`（修复问题 7）
- **[TranslationPipeline.java](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/task/TranslationPipeline.java)**：`@Value` 改为 `${mangaflow.pipeline.demo-enabled:true}`
- **[application-dev.yml:24](file:///d:/project/java_code/mangaflow-ai-translate/src/main/resources/application-dev.yml#L24)**：`com.mangaflow: debug` → `com.translate: debug`（日志包名修正）
- **[TranslationTaskServiceImpl.java](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/service/impl/TranslationTaskServiceImpl.java)**：L59 错误码 `NOT_FOUND` → `FILE_UPLOAD_ERROR`

### 2. 新增线程池配置（问题 2）

新建 **`src/main/java/com/translate/config/AsyncConfig.java`**：
- `@Configuration` 类，定义 `@Bean("translationExecutor")` 返回 `ThreadPoolTaskExecutor`
- 参数用 `@Value` 读 `mangaflow.async.executor.*`（core 4 / max 8 / queue 100 / keep-alive 60 / prefix `mangaflow-task-`，yml 已有）
- 拒绝策略 `CallerRunsPolicy`（队列满时回退同步执行，任务不丢失）
- `@EnableAsync` 已在主类上，不重复加

### 3. 状态机支持 progress / resultPath 落库（问题 3）

- **[TaskStateContext.java](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/statusMachine/TaskStateContext.java)**：新增 `Integer progress`、`String resultPath` 字段（含 getter/setter，`@Builder` 自动覆盖）
- **[TaskStateMachine.java](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/statusMachine/TaskStateMachine.java)**：构建 `updateEntity` 时（现有 errorMessage/retryCount 判断之后）同样按 `context.getProgress()` / `context.getResultPath()` 非空判断写入

### 4. TranslationPipeline 接入 AI（核心，问题 6）

改 **[TranslationPipeline.java](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/task/TranslationPipeline.java)**：
- 注入 `AiServiceClient`、`TranslationRegionMapper`
- `execute()` 新流程（严格沿状态机合法流转）：
  1. `fire(QUEUED→VALIDATING, 5%)`，读原图校验（现有逻辑保留）
  2. **demo 分支**：`demoEnabled=true` 时保持现有 `writeDemoResult` 画图流程（作为 Python 服务不可用时的回退）
  3. **AI 分支**（`demoEnabled=false`，替换现在"直接抛异常"的逻辑）：
     - `fire(VALIDATING→OCR_PROCESSING, 25%)` → 调用 `aiServiceClient.translate(原图绝对路径, sourceLang, targetLang)`（一次调用完成 OCR+翻译+渲染）
     - `fire(OCR_PROCESSING→TRANSLATING, 55%)` → **regions 落库**：先按 `task_id` 删除旧记录（重试幂等），再把 `response.getRegions()` 转 `TranslationRegion` 批量插入：`regionNo=i+1`、`originalText=region.text`、`translatedText=translations.get(i)`（`translations` 为空或长度不匹配时置 null、status=`OCR_DONE`，否则 `TRANSLATED`）；taskId 为 Long→Integer 强转（id 量级内安全）
     - `fire(TRANSLATING→IMAGE_RENDERING, 80%)` → 解码 base64 写文件：剥离可能的 `data:image/...;base64,` 前缀，用 `Base64.getMimeDecoder()`（容忍换行），`Files.write(createResultPath(taskNo))`，得到 resultPath
     - `fire(IMAGE_RENDERING→COMPLETED, 100%)`，context 带 `resultPath`
  4. 任一环节异常 → 现有 `markFailed`（不变）
- 内部 `fire(...)` helper 增加重载支持 resultPath 透传；删除"demo 关闭抛异常"逻辑
- demo 渲染路径的 `resultPath` 同样通过 `fire(...→COMPLETED, 100%, resultPath)` 落库（修复问题 3 对 demo 分支的影响）

### 5. Mapper XML 修复（问题 4）

改 **[TranslationTaskMapper.xml](file:///d:/project/java_code/mangaflow-ai-translate/src/main/resources/mapper/TranslationTaskMapper.xml)**：
- L5 namespace：`com.translate.mapper.TranslationTaskMapper` → `com.translate.dao.TranslationTaskMapper`
- L90 `markSuccess` 里 `stage = 'DONE'` → `stage = 'COMPLETED'`
- `TranslationRegionMapper.xml` namespace 正确，不动

### 6. 新增 schema.sql（问题 5）

新建 **`src/main/resources/schema.sql`**（dev 配置 `sql.init.mode: always` 已就位，默认扫描 classpath 根下的 schema.sql），全部 `CREATE TABLE IF NOT EXISTS` 保证幂等：
- `tb_translation_task`：`id BIGSERIAL PK`、`task_no VARCHAR(64) UNIQUE NOT NULL`、`status VARCHAR(32) NOT NULL`、`stage VARCHAR(32)`、`source_lang VARCHAR(16)`、`target_lang VARCHAR(16)`、`original_path VARCHAR(512)`、`result_path VARCHAR(512)`、`progress SMALLINT DEFAULT 0`、`error_message TEXT`、`retry_count INT DEFAULT 0`、`created_at/updated_at TIMESTAMP`；索引 `status`、`stage`
- `tb_translation_region`：`id BIGSERIAL PK`、`task_id BIGINT NOT NULL`、`region_no INT`、`x/y/width/height INT`、`original_text TEXT`、`translated_text TEXT`、`status VARCHAR(32) DEFAULT 'PENDING'`、`created_at/updated_at TIMESTAMP`、`UNIQUE(task_id, region_no)`；索引 `task_id`
- 已知取舍：`TranslationRegion` 实体 id/taskId 为 `Integer`，DDL 用 BIGINT，MyBatis 按实体类型取值，量级内安全，本次不扩实体

### 7. retry 逻辑修复（问题 8）+ 重试上限

改 **[TranslationTaskServiceImpl.java](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/service/impl/TranslationTaskServiceImpl.java)** 与 **[TranslationTaskController.java](file:///d:/project/java_code/mangaflow-ai-translate/src/main/java/com/translate/contrller/TranslationTaskController.java)**：
- `retryTask`：去掉传给状态机时的第二次 `+1`，直接用已 +1 的 `t.getRetryCount()`
- 新增上限检查：`retryCount >= max` 时抛 `TASK_RETRY_EXCEEDED`；`max` 来自新配置 `mangaflow.task.max-retry: 5`（加到 application.yml）
- Controller retry 接口 `ApiResponse.fail(...)` → `ApiResponse.success()`；Controller 里直接注入 Mapper 的用法本次不动（避免扩大改动面）

## 明确不做

- 不改 `contrller` 包名拼写、不做 `com.translate` → `com.mangaflow` 包重构
- 不做认证/鉴权/限流/CORS
- 不做任务列表接口、定时恢复、超时清理、文件清理调度
- 不做前端；不引入 Flyway（`sql.init` 够用）
- `PythonController`（同步调试通道）保持不动

## 验证步骤

1. `mvn -q compile` 编译通过
2. 启动应用（dev profile），确认 schema.sql 自动建表成功（日志无 SQL 错误）
3. 真实联调（Python 服务已就绪）：`DEMO_PIPELINE_ENABLED=false` 启动
   - `curl -F "file=@test.png" -F "sourceLang=ja" -F "targetLang=zh-CN" http://localhost:9001/api/v1/tasks` → 返回 taskId
   - 轮询 `GET /api/v1/tasks/{id}`：stage 依次推进、progress 递增，最终 `COMPLETED` 且 `resultAvailable=true`
   - `GET /api/v1/tasks/{id}/result`：下载到非空 PNG
   - 查库：`tb_translation_region` 有该任务的 regions 记录（含原文/译文/坐标）
4. demo 回退：`DEMO_PIPELINE_ENABLED=true` 重启，重复 3 的上传→轮询→下载（下载到带 Demo 标签的图）
5. 失败路径：停掉 Python 服务后上传 → 任务进入 `FAILED` 且 `error_message` 有内容 → `POST /api/v1/tasks/{id}/retry` 后恢复 Python 服务 → 任务最终 `COMPLETED`

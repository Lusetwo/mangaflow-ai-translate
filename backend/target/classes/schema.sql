-- MangaFlow 翻译任务库表结构（PostgreSQL）
-- dev 环境 spring.sql.init.mode=always，全部使用 IF NOT EXISTS 保证幂等

CREATE TABLE IF NOT EXISTS tb_translation_task (
    id            BIGSERIAL PRIMARY KEY,
    task_no       VARCHAR(64)  NOT NULL,
    status        VARCHAR(32)  NOT NULL DEFAULT 'PENDING'
                  CHECK (status IN ('PENDING','PROCESSING','SUCCESS','FAILED','MANUAL_REQUIRED')),
    stage         VARCHAR(32),
    source_lang   VARCHAR(16),
    target_lang   VARCHAR(16),
    original_path VARCHAR(512),
    result_path   VARCHAR(512),
    progress      SMALLINT     DEFAULT 0,
    error_message TEXT,
    retry_count   INT          DEFAULT 0,
    created_at    TIMESTAMP,
    updated_at    TIMESTAMP,
    CONSTRAINT uk_translation_task_no UNIQUE (task_no)
);

CREATE INDEX IF NOT EXISTS idx_translation_task_status ON tb_translation_task (status);
CREATE INDEX IF NOT EXISTS idx_translation_task_stage  ON tb_translation_task (stage);

CREATE TABLE IF NOT EXISTS tb_translation_region (
    id              BIGSERIAL PRIMARY KEY,
    task_id         BIGINT       NOT NULL,
    region_no       INT,
    x               INT,
    y               INT,
    width           INT,
    height          INT,
    original_text   TEXT,
    translated_text TEXT,
    status          VARCHAR(32)  DEFAULT 'PENDING',
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP,
    CONSTRAINT uk_translation_region_task_no UNIQUE (task_id, region_no),
    CONSTRAINT fk_translation_region_task FOREIGN KEY (task_id)
        REFERENCES tb_translation_task(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_translation_region_task ON tb_translation_region (task_id);

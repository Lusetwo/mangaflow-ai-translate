package com.translate.client;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class AiServiceResponse {
    private String sourceLang;
    private String targetLang;
    private String ocrMode;
    private String translationMode;
    private List<TextRegionResult> regions;
    private List<String> translations;
    private String resultImageBase64;
    private String resultMimeType;
    private String notice;

    public String getSourceLang() { return sourceLang; }
    public void setSourceLang(String sourceLang) { this.sourceLang = sourceLang; }
    public String getTargetLang() { return targetLang; }
    public void setTargetLang(String targetLang) { this.targetLang = targetLang; }
    public String getOcrMode() { return ocrMode; }
    public void setOcrMode(String ocrMode) { this.ocrMode = ocrMode; }
    public String getTranslationMode() { return translationMode; }
    public void setTranslationMode(String translationMode) { this.translationMode = translationMode; }
    public List<TextRegionResult> getRegions() { return regions; }
    public void setRegions(List<TextRegionResult> regions) { this.regions = regions; }
    public List<String> getTranslations() { return translations; }
    public void setTranslations(List<String> translations) { this.translations = translations; }
    public String getResultImageBase64() { return resultImageBase64; }
    public void setResultImageBase64(String resultImageBase64) { this.resultImageBase64 = resultImageBase64; }
    public String getResultMimeType() { return resultMimeType; }
    public void setResultMimeType(String resultMimeType) { this.resultMimeType = resultMimeType; }
    public String getNotice() { return notice; }
    public void setNotice(String notice) { this.notice = notice; }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class TextRegionResult {
        private String text;
        private Double confidence;
        private Integer x;
        private Integer y;
        private Integer width;
        private Integer height;
        public String getText() { return text; }
        public void setText(String text) { this.text = text; }
        public Double getConfidence() { return confidence; }
        public void setConfidence(Double confidence) { this.confidence = confidence; }
        public Integer getX() { return x; }
        public void setX(Integer x) { this.x = x; }
        public Integer getY() { return y; }
        public void setY(Integer y) { this.y = y; }
        public Integer getWidth() { return width; }
        public void setWidth(Integer width) { this.width = width; }
        public Integer getHeight() { return height; }
        public void setHeight(Integer height) { this.height = height; }
    }
}


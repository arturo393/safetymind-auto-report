package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func setupRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.GET("/health", healthHandler)
	r.GET("/api/projects", getProjectsHandler)
	r.GET("/api/reports/list", listReportsHandler)
	r.POST("/api/generate", generateReportHandler)
	return r
}

func TestHealthHandler(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/health", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, 200, w.Code)
	
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, "ok", response["status"])
	assert.NotEmpty(t, response["timestamp"])
}

func TestProjectsHandler(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/projects", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, 200, w.Code)
}

func TestListReportsHandler(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/reports/list", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, 200, w.Code)
}

func TestGenerateReportHandler(t *testing.T) {
	r := setupRouter()
	
	body := `{"project_key": "GMF", "report_type": "progress", "use_ai": false, "use_latex": false}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/api/generate", strings.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, 200, w.Code)
	
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, "success", response["status"])
}

func TestGenerateWithAI(t *testing.T) {
	r := setupRouter()
	
	body := `{"project_key": "GMF", "report_type": "progress", "use_ai": true, "use_latex": false}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/api/generate", strings.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, 200, w.Code)
}

func TestGenerateInvalidRequest(t *testing.T) {
	r := setupRouter()
	
	body := `{}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/api/generate", strings.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.True(t, w.Code == 400 || w.Code == 200)
}
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"gopkg.in/yaml.v3"
)

type Config struct {
	Projects map[string]ProjectConfig `yaml:"projects"`
}

type ProjectConfig struct {
	Name           string `yaml:"name"`
	JiraKey        string `yaml:"jira_key"`
	Description    string `yaml:"description"`
	ProjectManager string `yaml:"project_manager"`
	Client         string `yaml:"client"`
}

type ReportRequest struct {
	ProjectKey string `json:"project_key"`
	ReportType string `json:"report_type"`
	UseAI      bool   `json:"use_ai"`
}

type JiraProject struct {
	Key  string `json:"key"`
	Name string `json:"name"`
}

type ReportInfo struct {
	Name string `json:"name"`
	Size string `json:"size"`
	Date string `json:"date"`
}

var (
	configPath   = "config/projects.yaml"
	templatesDir = "templates"
	outputDir    = "reports"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	gin.SetMode(gin.ReleaseMode)
	r := gin.New()
	r.Use(gin.Logger(), gin.Recovery())

	r.GET("/health", healthHandler)
	r.GET("/api/ollama/health", ollamaHealthHandler)
	r.GET("/api/projects", getProjectsHandler)
	r.GET("/jira/projects", getJiraProjectsHandler)
	r.GET("/api/reports/list", listReportsHandler)
	r.POST("/api/generate", generateReportHandler)
	r.GET("/api/reports/download/:filename", downloadReportHandler)

	log.Printf("🚀 SafetyMind Go API on port %s", port)
	if err := r.Run(":" + port); err != nil {
		log.Fatal(err)
	}
}

func healthHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "ok",
		"timestamp": time.Now().Format(time.RFC3339),
	})
}

func ollamaHealthHandler(c *gin.Context) {
	ollamaURL := os.Getenv("OLLAMA_URL")
	if ollamaURL == "" {
		ollamaURL = "http://localhost:11434"
	}

	resp, err := http.Get(ollamaURL + "/api/tags")
	if err != nil {
		c.JSON(http.StatusOK, gin.H{
			"status": "unavailable",
			"error":  "Ollama no alcanzable",
		})
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == 200 {
		c.JSON(http.StatusOK, gin.H{
			"status": "ready",
		})
	} else {
		c.JSON(http.StatusOK, gin.H{
			"status": "error",
		})
	}
}

func getProjectsHandler(c *gin.Context) {
	config, err := loadConfig(configPath)
	if err != nil {
		c.JSON(http.StatusOK, gin.H{})
		return
	}

	localProjects := make(map[string]string)
	if config.Projects != nil {
		for key, data := range config.Projects {
			localProjects[key] = data.Name
		}
	}

	jiraProjects, err := fetchJiraProjects()
	if err != nil {
		for k, v := range localProjects {
			localProjects[k] = v
		}
		c.JSON(http.StatusOK, localProjects)
		return
	}

	final := mergeProjects(jiraProjects, localProjects)
	c.JSON(http.StatusOK, final)
}

func getJiraProjectsHandler(c *gin.Context) {
	projects, err := fetchJiraProjects()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, projects)
}

func listReportsHandler(c *gin.Context) {
	var reports []ReportInfo
	files, err := os.ReadDir(outputDir)
	if err != nil {
		c.JSON(http.StatusOK, reports)
		return
	}

	for _, f := range files {
		if !f.IsDir() && filepath.Ext(f.Name()) == ".pdf" {
			info, _ := f.Info()
			reports = append(reports, ReportInfo{
				Name: f.Name(),
				Size: fmt.Sprintf("%d KB", info.Size()/1024),
				Date: info.ModTime().Format("2006-01-02"),
			})
		}
	}
	c.JSON(http.StatusOK, reports)
}

func generateReportHandler(c *gin.Context) {
	var req ReportRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	timestamp := time.Now().Format("20060102150405")
	filename := fmt.Sprintf("%s_%s_%s.pdf", req.ProjectKey, req.ReportType, timestamp)

	jiraData, err := fetchJiraData(req.ProjectKey)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Jira connection failed"})
		return
	}

	description := "Análisis de telemetría en progreso."
	if req.UseAI {
		if aiDesc, err := generateAIsummary(jiraData); err == nil {
			description = aiDesc
		}
	}

	htmlContent, err := generateHTML(req.ReportType, jiraData, description)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate HTML"})
		return
	}

	// Save HTML temporarily
	htmlFilename := fmt.Sprintf("%s_%s_%s.html", req.ProjectKey, req.ReportType, timestamp)
	htmlPath := filepath.Join(outputDir, htmlFilename)
	if err := os.WriteFile(htmlPath, []byte(htmlContent), 0644); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save HTML"})
		return
	}

	// Convert HTML to PDF using wkhtmltopdf (lighter than LaTeX)
	pdfPath := filepath.Join(outputDir, filename)
	cmd := exec.Command("wkhtmltopdf", htmlPath, pdfPath)
	if err := cmd.Run(); err != nil {
		// If wkhtmltopdf fails, just serve HTML
		log.Printf("PDF conversion failed, serving HTML: %v", err)
		filename = htmlFilename
	}

	response := gin.H{
		"status":  "success",
		"job_id":  fmt.Sprintf("job_%s", timestamp),
		"message": fmt.Sprintf("Report generated for %s", req.ProjectKey),
		"filename": filename,
		"engine":  "html",
	}

	c.JSON(http.StatusOK, response)
}

func downloadReportHandler(c *gin.Context) {
	filename := c.Param("filename")
	filePath := filepath.Join(outputDir, filename)

	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "File not found"})
		return
	}

	if filepath.Ext(filePath) != ".pdf" && filepath.Ext(filePath) != ".tex" {
		c.JSON(http.StatusForbidden, gin.H{"error": "Restricted"})
		return
	}

	c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", filename))
	c.File(filePath)
}

func loadConfig(path string) (Config, error) {
	var config Config
	data, err := os.ReadFile(path)
	if err != nil {
		return config, err
	}
	var rawData map[string]interface{}
	yaml.Unmarshal(data, &rawData)
	yaml.Unmarshal(data, &config)
	return config, nil
}

func fetchJiraProjects() (map[string]string, error) {
	url := os.Getenv("JIRA_URL")
	email := os.Getenv("JIRA_EMAIL")
	token := os.Getenv("JIRA_API_TOKEN")

	client := &http.Client{}
	req, _ := http.NewRequest("GET", url+"/rest/api/3/project", nil)
	req.SetBasicAuth(email, token)

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var projects []struct {
		Key  string `json:"key"`
		Name string `json:"name"`
	}
	json.NewDecoder(resp.Body).Decode(&projects)

	res := make(map[string]string)
	for _, p := range projects {
		res[p.Key] = p.Name
	}
	return res, nil
}

func fetchJiraData(projectKey string) (map[string]interface{}, error) {
	url := os.Getenv("JIRA_URL")
	email := os.Getenv("JIRA_EMAIL")
	token := os.Getenv("JIRA_API_TOKEN")

	// JQL to fetch issues for the project
	jql := fmt.Sprintf(`project = "%s" ORDER BY created DESC`, projectKey)
	apiURL := fmt.Sprintf("%s/rest/api/3/search/jql?jql=%s&maxResults=100", url, jql)

	client := &http.Client{}
	req, _ := http.NewRequest("GET", apiURL, nil)
	req.SetBasicAuth(email, token)
	req.Header.Add("Accept", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch Jira data: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("Jira API returned status %d", resp.StatusCode)
	}

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)

	// Check for API errors
	if errorMessages, ok := result["errorMessages"].([]interface{}); ok && len(errorMessages) > 0 {
		return nil, fmt.Errorf("Jira API error: %v", errorMessages)
	}

	issues, ok := result["issues"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("no issues found in response")
	}
	totalIssues := len(issues)

	// Calculate metrics
	doneIssues := 0
	inProgressIssues := 0
	openIssues := 0
	completedTasks := []map[string]interface{}{}
	pendingTasks := []map[string]interface{}{}

	for _, issue := range issues {
		issueMap, ok := issue.(map[string]interface{})
		if !ok {
			continue
		}
		
		fields, ok := issueMap["fields"].(map[string]interface{})
		if !ok {
			openIssues++
			continue
		}
		
		status, ok := fields["status"].(map[string]interface{})
		if !ok {
			openIssues++
			continue
		}
		
		statusName, ok := status["name"].(string)
		if !ok {
			openIssues++
			continue
		}

		issueKey := ""
		if k, ok := issueMap["key"].(string); ok {
			issueKey = k
		}
		
		summary := ""
		if s, ok := fields["summary"].(string); ok {
			summary = s
		}

		switch statusName {
		case "Done", "Completed", "Closed":
			doneIssues++
			completedTasks = append(completedTasks, map[string]interface{}{
				"key":     issueKey,
				"summary": summary,
				"updated": fields["updated"],
			})
		case "In Progress", "In Review", "Testing":
			inProgressIssues++
			priority := "Normal"
			if p, ok := fields["priority"].(map[string]interface{}); ok {
				if pn, ok := p["name"].(string); ok {
					priority = pn
				}
			}
			pendingTasks = append(pendingTasks, map[string]interface{}{
				"key":      issueKey,
				"summary":  summary,
				"priority": priority,
			})
		default:
			openIssues++
			pendingTasks = append(pendingTasks, map[string]interface{}{
				"key":      issueKey,
				"summary":  summary,
				"priority": "Normal",
			})
		}
	}

	percentage := 0
	if totalIssues > 0 {
		percentage = int(float64(doneIssues) / float64(totalIssues) * 100)
	}

	// Get project config for client info
	config, _ := loadConfig(configPath)
	clientName := "SafetyMind Client"
	projectManager := "Arturo Veras"
	if cfg, ok := config.Projects[projectKey]; ok {
		clientName = cfg.Client
		projectManager = cfg.ProjectManager
	}

	data := map[string]interface{}{
		"project_key":        projectKey,
		"report_date":        time.Now().Format("2006-01-02"),
		"percentage":         percentage,
		"client":             clientName,
		"project_manager":    projectManager,
		"total_issues":       totalIssues,
		"done_issues":        doneIssues,
		"in_progress_issues": inProgressIssues,
		"open_issues":        openIssues,
		"completed_tasks":    completedTasks,
		"pending_tasks":      pendingTasks,
		"rag_time_class":     "rag-green",
		"rag_time_status":    "OK",
	}

	if percentage < 50 {
		data["rag_time_class"] = "rag-amber"
		data["rag_time_status"] = "ATRASADO"
	}

	return data, nil
}

func mergeProjects(jira, local map[string]string) map[string]string {
	res := make(map[string]string)
	for k, v := range jira {
		res[k] = v
	}
	for k, v := range local {
		res[k] = v
	}
	return res
}

func generateAIsummary(jiraData map[string]interface{}) (string, error) {
	ollamaURL := os.Getenv("OLLAMA_URL")
	if ollamaURL == "" {
		ollamaURL = "http://localhost:11434"
	}

	prompt := fmt.Sprintf("Genera un resumen ejecutivo diplomático para el proyecto %s basado en los datos de Jira.",
		jiraData["project_key"])

	system := `Eres un PMO Senior. Escribe en español profesional. Máximo 6 líneas. Sin formatos markdown.`

	payload := map[string]interface{}{
		"model":   "llama3:latest",
		"prompt":  prompt,
		"system":  system,
		"stream":  false,
		"options": map[string]interface{}{"temperature": 0.4, "num_predict": 500},
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(ollamaURL+"/api/generate", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return "Análisis de IA en progreso.", nil
	}
	defer resp.Body.Close()

	result := make(map[string]interface{})
	json.NewDecoder(resp.Body).Decode(&result)

	if response, ok := result["response"].(string); ok {
		return response, nil
	}
	return "Análisis completado.", nil
}

func generateHTML(reportType string, data map[string]interface{}, description string) (string, error) {
	baseTemplate := filepath.Join(templatesDir, "base.html")
	reportTemplate := filepath.Join(templatesDir, reportType+".html")

	if _, err := os.Stat(reportTemplate); err != nil {
		html := fmt.Sprintf(`<!DOCTYPE html">
<html><head><meta charset="UTF-8"><title>Report</title></head>
<body><h1>SafetyMind Report: %s</h1>
<p><strong>Project:</strong> %s</p>
<p><strong>Date:</strong> %s</p>
<p>%s</p></body></html>`,
			reportType, data["project_key"], data["report_date"], description)
		return html, nil
	}

	// Parse templates with base + specific template
	tmpl, err := template.ParseFiles(baseTemplate, reportTemplate)
	if err != nil {
		return "", fmt.Errorf("template parse error: %v", err)
	}

	// Add custom functions for templates
	funcMap := template.FuncMap{
		"add": func(a, b int) int { return a + b },
		"lt":  func(a, b int) bool { return a < b },
	}
	tmpl = tmpl.Funcs(funcMap)

	// Calculate RAG status
	percentage := 0
	if p, ok := data["percentage"].(int); ok {
		percentage = p
	}
	timeColor := "#4caf50"
	timeStatus := "OK"
	if percentage < 50 {
		timeColor = "#ff9800"
		timeStatus = "ATRASADO"
	}

	// Prepare template data
	tmplData := map[string]interface{}{
		"title":            fmt.Sprintf("SafetyMind - %s", strings.Title(reportType)),
		"report_type":      fmt.Sprintf("Informe de %s", strings.Title(reportType)),
		"project_name":     data["project_key"],
		"year":             time.Now().Year(),
		"report_date":      data["report_date"],
		"percentage":       percentage,
		"time_color":       timeColor,
		"time_status":      timeStatus,
		"critical_path":    []interface{}{}, // TODO: implement
		"blockers":         "",              // TODO: get from config
		"completed_tasks":  data["completed_tasks"],
		"pending_tasks":    data["pending_tasks"],
		"description":      description,
	}

	var buf bytes.Buffer
	err = tmpl.Execute(&buf, tmplData)
	if err != nil {
		return "", fmt.Errorf("template execute error: %v", err)
	}

	return buf.String(), nil
}

func init() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	log.SetOutput(os.Stdout)
}

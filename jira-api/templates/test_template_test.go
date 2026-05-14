package main

import (
	"bytes"
	"html/template"
	"testing"
	"time"
)

func TestProgressTemplate(t *testing.T) {
	// Parse templates
	tmpl, err := template.ParseFiles("templates/base.html", "templates/progress.html")
	if err != nil {
		t.Fatalf("Failed to parse templates: %v", err)
	}

	// Test data
	tmplData := map[string]interface{}{
		"title":           "SafetyMind - Informe de Avance",
		"report_type":     "Informe de Avance",
		"project_name":    "IM",
		"year":            time.Now().Year(),
		"report_date":     "2026-05-06",
		"percentage":      75,
		"time_color":      "#4caf50",
		"time_status":     "OK",
		"critical_path":   []interface{}{},
		"blockers":        "",
		"completed_tasks": []interface{}{},
		"pending_tasks":   []interface{}{},
		"description":     "Test description",
	}

	var buf bytes.Buffer
	err = tmpl.Execute(&buf, tmplData)
	if err != nil {
		t.Fatalf("Failed to execute template: %v", err)
	}

	html := buf.String()
	
	// Verify key elements are present
	expectedStrings := []string{
		"SafetyMind - Informe de Avance",
		"Proyecto: IM",
		"75%",
		"OK",
		"Test description",
	}

	for _, expected := range expectedStrings {
		if !bytes.Contains([]byte(html), []byte(expected)) {
			t.Errorf("Expected string not found in output: %s", expected)
		}
	}
}

func TestTemplateWithTasks(t *testing.T) {
	tmpl, err := template.ParseFiles("templates/base.html", "templates/progress.html")
	if err != nil {
		t.Fatalf("Failed to parse templates: %v", err)
	}

	completedTasks := []map[string]interface{}{
		{"key": "IM-1", "summary": "Task 1", "updated": "2026-05-01"},
		{"key": "IM-2", "summary": "Task 2", "updated": "2026-05-02"},
	}
	pendingTasks := []map[string]interface{}{
		{"summary": "Pending 1", "priority": "High"},
		{"summary": "Pending 2", "priority": "Medium"},
	}

	tmplData := map[string]interface{}{
		"title":           "SafetyMind - Informe de Avance",
		"report_type":     "Informe de Avance",
		"project_name":    "IM",
		"year":            time.Now().Year(),
		"report_date":     "2026-05-06",
		"percentage":      50,
		"time_color":      "#ff9800",
		"time_status":     "ATRASADO",
		"critical_path":   []interface{}{},
		"blockers":        "",
		"completed_tasks": completedTasks,
		"pending_tasks":   pendingTasks,
		"description":     "",
	}

	var buf bytes.Buffer
	err = tmpl.Execute(&buf, tmplData)
	if err != nil {
		t.Fatalf("Failed to execute template: %v", err)
	}

	html := buf.String()

	// Verify tasks are present
	expectedStrings := []string{
		"IM-1",
		"Task 1",
		"Pending 1",
		"ATRASADO",
		"No hay bloqueos activos reportados",
	}

	for _, expected := range expectedStrings {
		if !bytes.Contains([]byte(html), []byte(expected)) {
			t.Errorf("Expected string not found in output: %s", expected)
		}
	}
}

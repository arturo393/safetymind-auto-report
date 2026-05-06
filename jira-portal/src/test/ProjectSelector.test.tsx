import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ProjectSelector } from '../components/molecules/ProjectSelector'

describe('ProjectSelector Molecule', () => {
  const mockProjects = { 'GMF': 'Proyecto GMF', 'IM': 'Infra Monitoring' }
  const mockSetActive = vi.fn()
  const mockOnGenerate = vi.fn()

  it('renders correctly with industrial labels', () => {
    render(
      <ProjectSelector 
        projects={mockProjects}
        activeProject=""
        setActiveProject={mockSetActive}
        onGenerate={mockOnGenerate}
        isGenerating={false}
      />
    )
    
    expect(screen.getByText(/PROYECTO ACTIVO/i)).toBeInTheDocument()
    expect(screen.getByText(/INICIAR REPORTE/i)).toBeInTheDocument()
  })

  it('disables the generate button when no project is selected', () => {
    render(
      <ProjectSelector 
        projects={mockProjects}
        activeProject=""
        setActiveProject={mockSetActive}
        onGenerate={mockOnGenerate}
        isGenerating={false}
      />
    )
    
    const btn = screen.getByRole('button', { name: /Iniciar generación de reporte industrial/i })
    expect(btn).toBeDisabled()
  })

  it('calls onGenerate when clicked and project is active', () => {
     render(
      <ProjectSelector 
        projects={mockProjects}
        activeProject="GMF"
        setActiveProject={mockSetActive}
        onGenerate={mockOnGenerate}
        isGenerating={false}
      />
    )
    
    const btn = screen.getByRole('button', { name: /Iniciar generación de reporte industrial/i })
    fireEvent.click(btn)
    expect(mockOnGenerate).toHaveBeenCalled()
  })
})

import { useState, useCallback } from 'react'
import { projectsApi } from '../api/index.js'

export function useProject() {
  const [project,    setProject]    = useState(null)
  const [milestones, setMilestones] = useState([])
  const [loading,    setLoading]    = useState(false)
  const [error,      setError]      = useState(null)

  const fetchProject = useCallback(async (id) => {
    setLoading(true)
    setError(null)
    try {
      const [{ data: proj }, { data: ms }] = await Promise.all([
        projectsApi.getById(id),
        projectsApi.getMilestones(id),
      ])
      setProject(proj)
      setMilestones(ms)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to load project.')
    } finally {
      setLoading(false)
    }
  }, [])

  const createProject = useCallback(async (data) => {
    const { data: created } = await projectsApi.create(data)
    return created
  }, [])

  const updateProject = useCallback(async (id, data) => {
    const { data: updated } = await projectsApi.update(id, data)
    setProject(updated)
    return updated
  }, [])

  const completeProject = useCallback(async (id) => {
    const { data: completed } = await projectsApi.complete(id)
    setProject(completed)
    return completed
  }, [])

  const addMilestone = useCallback(async (projectId, data) => {
    const { data: milestone } = await projectsApi.createMilestone(projectId, data)
    setMilestones((prev) => [...prev, milestone])
    return milestone
  }, [])

  return {
    project,
    milestones,
    loading,
    error,
    fetchProject,
    createProject,
    updateProject,
    completeProject,
    addMilestone,
  }
}
import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import {
  Eye, ExternalLink, Github, Pencil,
  Trash2, CheckCircle, AlertTriangle,
} from 'lucide-react'
import { projectsApi, commentsApi } from '../api/index.js'
import { useAuthStore } from '../store/authStore.js'
import { useToast, Avatar, Badge, Button, Modal, Spinner, EmptyState } from '../components/ui/index.js'
import { CollabButton, MilestoneList, MilestoneForm, StageSelector } from '../components/project/index.js'
import { CommentThread } from '../components/comments/index.js'
import clsx from 'clsx'

const stageGradients = {
  idea:      'from-gray-100 to-gray-200',
  building:  'from-brand-tint to-green-200',
  testing:   'from-orange-50 to-orange-100',
  shipped:   'from-blue-50 to-blue-100',
  completed: 'from-green-100 to-green-200',
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-ZA', {
    day: 'numeric', month: 'long', year: 'numeric',
  })
}

export default function ProjectDetail() {
  const { id }       = useParams()
  const navigate     = useNavigate()
  const toast        = useToast()
  const { user, isAuthenticated } = useAuthStore()

  const [project,      setProject]      = useState(null)
  const [milestones,   setMilestones]   = useState([])
  const [comments,     setComments]     = useState([])
  const [loading,      setLoading]      = useState(true)

  const [showMilestoneForm, setShowMilestoneForm] = useState(false)
  const [showCompleteModal, setShowCompleteModal] = useState(false)
  const [showDeleteModal,   setShowDeleteModal]   = useState(false)
  const [completing,        setCompleting]        = useState(false)
  const [deleting,          setDeleting]          = useState(false)

  const isOwner = user?.id === project?.owner_id

  // ── Load all project data ──────────────────────────────────────────────
  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [{ data: proj }, { data: ms }, { data: cmts }] = await Promise.all([
        projectsApi.getById(id),
        projectsApi.getMilestones(id),
        commentsApi.list(id),
      ])
      setProject(proj)
      setMilestones(ms)

      // Nest replies under their parent comments
      const topLevel = (cmts.items ?? cmts).filter((c) => !c.parent_id)
      const replies  = (cmts.items ?? cmts).filter((c) =>  c.parent_id)
      const nested   = topLevel.map((c) => ({
        ...c,
        replies: replies.filter((r) => r.parent_id === c.id),
      }))
      setComments(nested)
    } catch {
      toast('Failed to load project.', 'error')
      navigate('/feed')
    } finally {
      setLoading(false)
    }
  }, [id, navigate, toast])

  useEffect(() => { load() }, [load])

  // ── Milestone add ──────────────────────────────────────────────────────
  const handleAddMilestone = async (data) => {
    const { data: milestone } = await projectsApi.createMilestone(id, data)
    setMilestones((prev) => [...prev, milestone])
    setShowMilestoneForm(false)
  }

  // ── Complete project ───────────────────────────────────────────────────
  const handleComplete = async () => {
    setCompleting(true)
    try {
      const { data: completed } = await projectsApi.complete(id)
      setProject(completed)
      setShowCompleteModal(false)
      toast('🎉 Project marked as completed!', 'success')
    } catch (err) {
      const detail = err.response?.data?.detail ?? 'Failed to complete project.'
      toast(detail, 'error')
    } finally {
      setCompleting(false)
    }
  }

  // ── Delete project ─────────────────────────────────────────────────────
  const handleDelete = async () => {
    setDeleting(true)
    try {
      await projectsApi.delete(id)
      toast('Project deleted.', 'success')
      navigate('/feed')
    } catch {
      toast('Failed to delete project.', 'error')
    } finally {
      setDeleting(false)
    }
  }

  // ── Loading ────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!project) return null

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">

      {/* ── Cover header ── */}
      <div className={clsx(
        'h-56 rounded-xl bg-gradient-to-br mb-8 overflow-hidden relative',
        stageGradients[project.stage] ?? stageGradients.idea
      )}>
        {project.cover_image_url && (
          <img
            src={project.cover_image_url}
            alt={`${project.title} cover`}
            className="w-full h-full object-cover"
          />
        )}

        {/* View count overlay */}
        <div className="absolute bottom-3 right-4 flex items-center gap-1.5 bg-black/50 text-white text-xs px-2.5 py-1 rounded-full">
          <Eye className="w-3.5 h-3.5" />
          {project.view_count ?? 0} views
        </div>
      </div>

      {/* ── Project header ── */}
      <div className="flex flex-col gap-6 mb-10">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex flex-col gap-2 flex-1">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl font-bold text-text-primary">{project.title}</h1>
              <Badge variant="stage" stage={project.stage} />
            </div>

            {/* Owner */}
            <Link
              to={`/profile/${project.owner?.username}`}
              className="flex items-center gap-2 w-fit hover:opacity-80 transition-opacity"
            >
              <Avatar
                src={project.owner?.avatar_url}
                name={project.owner?.display_name}
                size="sm"
              />
              <span className="text-sm font-medium text-text-body">
                {project.owner?.display_name}
              </span>
            </Link>

            <p className="text-xs text-text-muted">
              Started {formatDate(project.created_at)}
            </p>
          </div>

          {/* Owner actions */}
          {isOwner && (
            <div className="flex items-center gap-2 flex-wrap">
              {project.stage !== 'completed' && (
                <>
                  <Link to={`/projects/${id}/edit`}>
                    <Button variant="ghost" size="sm">
                      <Pencil className="w-4 h-4" /> Edit
                    </Button>
                  </Link>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => setShowCompleteModal(true)}
                  >
                    <CheckCircle className="w-4 h-4" /> Mark complete
                  </Button>
                </>
              )}
              <Button
                variant="danger"
                size="sm"
                onClick={() => setShowDeleteModal(true)}
              >
                <Trash2 className="w-4 h-4" /> Delete
              </Button>
            </div>
          )}

          {/* Collab button — non-owners */}
          {!isOwner && <CollabButton project={project} />}
        </div>

        {/* Links */}
        {(project.repo_url || project.live_url) && (
          <div className="flex gap-3 flex-wrap">
            {project.repo_url && (
              
                href={project.repo_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-sm text-text-body hover:text-brand-primary transition-colors"
              >
                <Github className="w-4 h-4" /> Repository
              </a>
            )}
            {project.live_url && (
              
                href={project.live_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-sm text-text-body hover:text-brand-primary transition-colors"
              >
                <ExternalLink className="w-4 h-4" /> Live site
              </a>
            )}
          </div>
        )}

        {/* Tech stack */}
        {project.tech_stack?.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {project.tech_stack.map((tech) => (
              <Badge key={tech} label={tech} variant="tag" />
            ))}
          </div>
        )}

        {/* Support tags */}
        {project.support_tags?.length > 0 && (
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-xs text-text-muted font-medium">Needs:</span>
            {project.support_tags.map((tag) => (
              <span
                key={tag}
                className="text-xs px-2.5 py-1 rounded-full bg-surface-offwhite text-text-muted border border-ui-border"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Stage selector — owner only, not completed */}
        {isOwner && project.stage !== 'completed' && (
          <div className="p-4 bg-surface-white rounded-lg border border-ui-border">
            <StageSelector
              value={project.stage}
              onChange={async (newStage) => {
                try {
                  const { data: updated } = await projectsApi.update(id, { stage: newStage })
                  setProject(updated)
                  toast('Stage updated.', 'success')
                } catch {
                  toast('Failed to update stage.', 'error')
                }
              }}
            />
          </div>
        )}
      </div>

      {/* ── Two column layout on desktop ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">

        {/* Main column */}
        <div className="lg:col-span-2 flex flex-col gap-10">

          {/* Description */}
          {project.description && (
            <section>
              <h2 className="text-lg font-semibold text-text-primary mb-4">About</h2>
              <div className="prose prose-sm max-w-none text-text-body
                prose-headings:text-text-primary prose-a:text-brand-primary
                prose-code:text-brand-primary prose-code:bg-brand-tint
                prose-code:px-1 prose-code:rounded">
                <ReactMarkdown>{project.description}</ReactMarkdown>
              </div>
            </section>
          )}

          {/* Comments */}
          <section className="border-t border-ui-border pt-8">
            <CommentThread
              projectId={id}
              projectOwnerId={project.owner_id}
              comments={comments}
              onCommentsChange={setComments}
            />
          </section>
        </div>

        {/* Sidebar column */}
        <div className="flex flex-col gap-6">

          {/* Milestones */}
          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary">
                Milestones
              </h2>
              {isOwner && project.stage !== 'completed' && (
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => setShowMilestoneForm((v) => !v)}
                >
                  {showMilestoneForm ? 'Cancel' : '+ Add'}
                </Button>
              )}
            </div>

            {showMilestoneForm && (
              <div className="mb-6 animate-fade-in">
                <MilestoneForm
                  projectId={id}
                  onMilestoneAdded={handleAddMilestone}
                />
              </div>
            )}

            <MilestoneList milestones={milestones} />
          </section>

        </div>
      </div>

      {/* ── Complete confirmation modal ── */}
      <Modal
        isOpen={showCompleteModal}
        onClose={() => setShowCompleteModal(false)}
        title="Mark project as completed"
        size="md"
      >
        <div className="flex flex-col gap-4">
          <div className="flex gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <AlertTriangle className="w-5 h-5 text-yellow-600 shrink-0 mt-0.5" />
            <p className="text-sm text-yellow-800 leading-relaxed">
              This action is <strong>irreversible</strong>. Once marked as completed,
              this project will be locked and added to the Celebration Wall.
            </p>
          </div>
          <p className="text-sm text-text-body">
            Are you sure you want to mark <strong>"{project.title}"</strong> as completed?
          </p>
          <div className="flex gap-3 justify-end pt-2">
            <Button
              variant="ghost"
              onClick={() => setShowCompleteModal(false)}
              disabled={completing}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              loading={completing}
              onClick={handleComplete}
            >
              <CheckCircle className="w-4 h-4" />
              Yes, mark complete
            </Button>
          </div>
        </div>
      </Modal>

      {/* ── Delete confirmation modal ── */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete project"
        size="md"
      >
        <div className="flex flex-col gap-4">
          <div className="flex gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <p className="text-sm text-red-800 leading-relaxed">
              This will permanently delete <strong>"{project.title}"</strong> including
              all milestones, comments, and collaboration requests. This cannot be undone.
            </p>
          </div>
          <div className="flex gap-3 justify-end pt-2">
            <Button
              variant="ghost"
              onClick={() => setShowDeleteModal(false)}
              disabled={deleting}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              loading={deleting}
              onClick={handleDelete}
            >
              <Trash2 className="w-4 h-4" />
              Delete project
            </Button>
          </div>
        </div>
      </Modal>

    </div>
  )
}
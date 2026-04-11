import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { ImagePlus, X } from 'lucide-react'
import { projectsApi } from '../api/index.js'
import { useAuthStore } from '../store/authStore.js'
import { useToast, Input, Textarea, Button, Spinner } from '../components/ui/index.js'
import { StageSelector, TagInput } from '../components/project/index.js'

const MAX_FILE_SIZE = 5 * 1024 * 1024

export default function EditProject() {
  const { id }     = useParams()
  const navigate   = useNavigate()
  const toast      = useToast()
  const { user }   = useAuthStore()

  const [project,     setProject]     = useState(null)
  const [pageLoading, setPageLoading] = useState(true)
  const [saving,      setSaving]      = useState(false)

  const [stage,        setStage]        = useState('idea')
  const [techStack,    setTechStack]    = useState([])
  const [supportTags,  setSupportTags]  = useState([])
  const [coverFile,    setCoverFile]    = useState(null)
  const [coverPreview, setCoverPreview] = useState(null)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({ mode: 'onBlur' })

  // Load project
  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await projectsApi.getById(id)

        // Redirect if not owner
        if (data.owner_id !== user?.id) {
          toast('You do not have permission to edit this project.', 'error')
          navigate(`/projects/${id}`)
          return
        }

        // Redirect if completed — completed projects are locked
        if (data.stage === 'completed') {
          toast('Completed projects cannot be edited.', 'info')
          navigate(`/projects/${id}`)
          return
        }

        setProject(data)
        setStage(data.stage)
        setTechStack(data.tech_stack   ?? [])
        setSupportTags(data.support_tags ?? [])
        setCoverPreview(data.cover_image_url ?? null)

        reset({
          title:       data.title,
          description: data.description ?? '',
          repo_url:    data.repo_url    ?? '',
          live_url:    data.live_url    ?? '',
        })
      } catch {
        toast('Failed to load project.', 'error')
        navigate('/feed')
      } finally {
        setPageLoading(false)
      }
    }

    load()
  }, [id, user?.id, navigate, reset, toast])

  // Cover image
  const handleCoverChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > MAX_FILE_SIZE) {
      toast('Cover image must be under 5MB.', 'error')
      return
    }
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      toast('Only JPEG, PNG, or WebP images are allowed.', 'error')
      return
    }

    setCoverFile(file)
    setCoverPreview(URL.createObjectURL(file))
  }

  const removeCover = () => {
    setCoverFile(null)
    setCoverPreview(null)
  }

  // ── Submit ─────────────────────────────────────────────────────────────
  const onSubmit = async (data) => {
    setSaving(true)
    try {
      await projectsApi.update(id, {
        title:        data.title,
        description:  data.description,
        stage,
        tech_stack:   techStack,
        support_tags: supportTags,
        repo_url:     data.repo_url  || undefined,
        live_url:     data.live_url  || undefined,
      })

      if (coverFile) {
        try {
          await projectsApi.uploadCover(id, coverFile)
        } catch {
          toast('Project saved but cover upload failed.', 'info')
        }
      }

      toast('Project updated!', 'success')
      navigate(`/projects/${id}`)
    } catch (err) {
      const detail = err.response?.data?.detail ?? 'Failed to update project.'
      toast(detail, 'error')
    } finally {
      setSaving(false)
    }
  }

  // Loading state
  if (pageLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-text-primary">Edit project</h1>
        <p className="text-text-muted mt-1 text-sm">
          Updating: <span className="font-medium text-text-primary">{project?.title}</span>
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-6">

        {/* Cover image */}
        <div className="flex flex-col gap-1">
          <span className="text-sm font-medium text-text-primary">Cover image</span>

          {coverPreview ? (
            <div className="relative rounded-lg overflow-hidden h-48 bg-surface-offwhite border border-ui-border">
              <img
                src={coverPreview}
                alt="Cover preview"
                className="w-full h-full object-cover"
              />
              <button
                type="button"
                onClick={removeCover}
                aria-label="Remove cover image"
                className="absolute top-2 right-2 p-1.5 rounded-full bg-black/60 text-white hover:bg-black/80 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <label className="flex flex-col items-center justify-center h-48 rounded-lg border-2 border-dashed border-ui-border bg-surface-offwhite hover:border-brand-primary hover:bg-brand-tint transition-colors cursor-pointer">
              <ImagePlus className="w-8 h-8 text-text-muted mb-2" />
              <span className="text-sm text-text-muted">Click to upload cover image</span>
              <span className="text-xs text-text-muted mt-1">JPEG, PNG, WebP — max 5MB</span>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleCoverChange}
                className="sr-only"
                aria-label="Upload cover image"
              />
            </label>
          )}
        </div>

        {/* Title */}
        <Input
          label="Project title"
          required
          error={errors.title?.message}
          {...register('title', {
            required:  'Project title is required',
            minLength: { value: 3,   message: 'At least 3 characters' },
            maxLength: { value: 200, message: 'Max 200 characters' },
          })}
        />

        {/* Description */}
        <Textarea
          label="Description"
          rows={5}
          hint="Markdown is supported."
          error={errors.description?.message}
          {...register('description', {
            maxLength: { value: 5000, message: 'Max 5000 characters' },
          })}
        />

        {/* Stage selector */}
        <StageSelector
          value={stage}
          onChange={setStage}
        />

        {/* Tech stack */}
        <TagInput
          label="Tech stack"
          value={techStack}
          onChange={setTechStack}
          placeholder="React, Python, PostgreSQL..."
          hint="Press Enter or comma to add. Max 15 tags."
          max={15}
        />

        {/* Support tags */}
        <TagInput
          label="Support needed"
          value={supportTags}
          onChange={setSupportTags}
          placeholder="code-review, design, testing..."
          hint="What kind of help are you looking for? Max 10 tags."
          max={10}
        />

        {/* URLs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Repository URL"
            type="url"
            placeholder="https://github.com/..."
            error={errors.repo_url?.message}
            {...register('repo_url', {
              pattern: {
                value:   /^https?:\/\/.+/,
                message: 'Must be a valid URL',
              },
            })}
          />
          <Input
            label="Live URL"
            type="url"
            placeholder="https://myproject.com"
            error={errors.live_url?.message}
            {...register('live_url', {
              pattern: {
                value:   /^https?:\/\/.+/,
                message: 'Must be a valid URL',
              },
            })}
          />
        </div>

        {/* Actions */}
        <div className="flex gap-3 justify-end pt-2 border-t border-ui-border">
          <Button
            type="button"
            variant="ghost"
            onClick={() => navigate(`/projects/${id}`)}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            loading={saving}
            size="lg"
          >
            Save changes
          </Button>
        </div>

      </form>
    </div>
  )
}
import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import {
  Github, Globe, Pencil, Check, X,
  Camera, Users, FolderOpen, Clock,
} from 'lucide-react'
import { usersApi, collaborationsApi, projectsApi } from '../api/index.js'
import { useAuthStore } from '../store/authStore.js'
import { useToast, Avatar, Badge, Button, Input, Textarea, Spinner, EmptyState, Modal } from '../components/ui/index.js'
import { ProjectCard } from '../components/project/index.js'

const MAX_AVATAR_SIZE = 5 * 1024 * 1024

// Skill tag input
function SkillsInput({ value = [], onChange }) {
  const [input, setInput] = useState('')

  const add = (raw) => {
    const skill = raw.trim()
    if (!skill || value.includes(skill) || value.length >= 20) return
    onChange([...value, skill])
    setInput('')
  }

  const remove = (skill) => onChange(value.filter((s) => s !== skill))

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-2 min-h-[36px]">
        {value.map((skill) => (
          <span
            key={skill}
            className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-brand-tint text-brand-primary border border-brand-border"
          >
            {skill}
            <button
              type="button"
              onClick={() => remove(skill)}
              aria-label={`Remove ${skill}`}
              className="hover:text-red-500 transition-colors"
            >
              <X className="w-3 h-3" />
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (['Enter', ','].includes(e.key)) {
              e.preventDefault()
              add(input)
            }
          }}
          placeholder="Add a skill and press Enter..."
          className="flex-1 px-3 py-1.5 rounded border border-ui-border text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-primary"
          aria-label="Add skill"
        />
        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={() => add(input)}
        >
          Add
        </Button>
      </div>
    </div>
  )
}

// ── Collab request card ───────────────────────────────────────────────────
function CollabRequestCard({ request, onRespond }) {
  const [loading, setLoading] = useState(false)

  const handle = async (status) => {
    setLoading(true)
    try {
      await onRespond(request.project_id, request.id, status)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 bg-surface-white rounded-lg border border-ui-border flex flex-col gap-3">
      <div className="flex items-start gap-3">
        <Avatar
          src={request.requester?.avatar_url}
          name={request.requester?.display_name}
          size="sm"
        />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-text-primary">
            {request.requester?.display_name}
          </p>
          <p className="text-xs text-text-muted">
            wants to collaborate on{' '}
            <Link
              to={`/projects/${request.project_id}`}
              className="text-brand-primary hover:underline font-medium"
            >
              {request.project_title ?? 'your project'}
            </Link>
          </p>
        </div>
        <span className="text-xs text-text-muted shrink-0 px-2 py-0.5 rounded-full bg-yellow-50 border border-yellow-200 text-yellow-700">
          Pending
        </span>
      </div>

      {request.message && (
        <p className="text-sm text-text-body italic bg-surface-offwhite px-3 py-2 rounded">
          "{request.message}"
        </p>
      )}

      <div className="flex gap-2 justify-end">
        <Button
          size="sm"
          variant="ghost"
          disabled={loading}
          onClick={() => handle('declined')}
        >
          <X className="w-4 h-4" /> Decline
        </Button>
        <Button
          size="sm"
          loading={loading}
          onClick={() => handle('accepted')}
        >
          <Check className="w-4 h-4" /> Accept
        </Button>
      </div>
    </div>
  )
}

// Main page
export default function Profile() {
  const { username }  = useParams()
  const navigate      = useNavigate()
  const toast         = useToast()
  const { user: me, isAuthenticated, updateUser } = useAuthStore()

  const isOwnProfile =
    !username ||
    username === 'me' ||
    username === me?.username

  const [profile,       setProfile]       = useState(null)
  const [projects,      setProjects]      = useState([])
  const [collabReqs,    setCollabReqs]    = useState([])
  const [loading,       setLoading]       = useState(true)
  const [editing,       setEditing]       = useState(false)
  const [savingProfile, setSavingProfile] = useState(false)
  const [skills,        setSkills]        = useState([])
  const [avatarLoading, setAvatarLoading] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm()

  // Load profile
  const load = useCallback(async () => {
    setLoading(true)
    try {
      let profileData

      if (isOwnProfile) {
        const { data } = await usersApi.me()
        profileData = data
      } else {
        const { data } = await usersApi.getByUsername(username)
        profileData = data
      }

      setProfile(profileData)
      setSkills(profileData.skills ?? [])

      reset({
        display_name: profileData.display_name ?? '',
        bio:          profileData.bio           ?? '',
        github_url:   profileData.github_url    ?? '',
        website_url:  profileData.website_url   ?? '',
      })

      // Load their projects
      const { data: projData } = await usersApi.getUserProjects(
        profileData.username,
        { limit: 20 }
      )
      setProjects(projData.items ?? projData)

      // Load pending collab requests for own profile
      if (isOwnProfile && profileData.projects?.length > 0) {
        // Fetch collab requests per project — collect pending ones
        const allRequests = []
        for (const proj of (projData.items ?? projData).slice(0, 10)) {
          try {
            const { data: reqs } = await collaborationsApi.list(proj.id)
            const pending = (reqs.items ?? reqs)
              .filter((r) => r.status === 'pending')
              .map((r) => ({ ...r, project_id: proj.id, project_title: proj.title }))
            allRequests.push(...pending)
          } catch {
            // Project may have no requests — skip
          }
        }
        setCollabReqs(allRequests)
      }
    } catch {
      toast('Failed to load profile.', 'error')
      navigate('/feed')
    } finally {
      setLoading(false)
    }
  }, [isOwnProfile, username, reset, toast, navigate])

  useEffect(() => { load() }, [load])

  // Save profile
  const onSave = async (data) => {
    setSavingProfile(true)
    try {
      const { data: updated } = await usersApi.updateProfile({
        display_name: data.display_name,
        bio:          data.bio          || undefined,
        github_url:   data.github_url   || undefined,
        website_url:  data.website_url  || undefined,
        skills,
      })
      setProfile(updated)
      updateUser(updated)
      setEditing(false)
      toast('Profile updated!', 'success')
    } catch {
      toast('Failed to update profile.', 'error')
    } finally {
      setSavingProfile(false)
    }
  }

  // Avatar upload
  const handleAvatarChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > MAX_AVATAR_SIZE) {
      toast('Avatar must be under 5MB.', 'error')
      return
    }
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      toast('Only JPEG, PNG, or WebP images are allowed.', 'error')
      return
    }

    setAvatarLoading(true)
    try {
      const { data: updated } = await usersApi.uploadAvatar(file)
      setProfile((prev) => ({ ...prev, avatar_url: updated.avatar_url }))
      updateUser({ avatar_url: updated.avatar_url })
      toast('Avatar updated!', 'success')
    } catch {
      toast('Failed to upload avatar.', 'error')
    } finally {
      setAvatarLoading(false)
    }
  }

  // Collab request response
  const handleCollabRespond = async (projectId, requestId, status) => {
    try {
      await collaborationsApi.respond(projectId, requestId, status)
      setCollabReqs((prev) => prev.filter((r) => r.id !== requestId))
      toast(
        status === 'accepted' ? 'Collaboration accepted!' : 'Request declined.',
        status === 'accepted' ? 'success' : 'info'
      )
    } catch {
      toast('Failed to respond to request.', 'error')
    }
  }

  // Loading
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!profile) return null

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* ── Left column — profile card ── */}
        <div className="lg:col-span-1">
          <div className="bg-surface-white rounded-lg border border-ui-border p-6 flex flex-col gap-5 sticky top-24">

            {/* Avatar */}
            <div className="flex flex-col items-center gap-3">
              <div className="relative">
                <Avatar
                  src={profile.avatar_url}
                  name={profile.display_name}
                  size="xl"
                />
                {isOwnProfile && (
                  <label
                    aria-label="Upload new avatar"
                    className="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-surface-dark border-2 border-white flex items-center justify-center cursor-pointer hover:bg-gray-700 transition-colors"
                  >
                    {avatarLoading
                      ? <Spinner size="sm" color="inherit" />
                      : <Camera className="w-4 h-4 text-white" />
                    }
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      onChange={handleAvatarChange}
                      className="sr-only"
                    />
                  </label>
                )}
              </div>

              {/* Name + username */}
              {!editing ? (
                <div className="text-center">
                  <h1 className="text-lg font-bold text-text-primary">
                    {profile.display_name}
                  </h1>
                  <p className="text-sm text-text-muted">@{profile.username}</p>
                </div>
              ) : null}
            </div>

            {/* ── View mode ── */}
            {!editing && (
              <>
                {profile.bio && (
                  <p className="text-sm text-text-body leading-relaxed text-center">
                    {profile.bio}
                  </p>
                )}

                {/* Links */}
                <div className="flex flex-col gap-2">
                  {profile.github_url && (
                    
                    <a  href={profile.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-sm text-text-body hover:text-brand-primary transition-colors"
                    >
                      <Github className="w-4 h-4 shrink-0" />
                      <span className="truncate">GitHub</span>
                    </a>
                  )}
                  {profile.website_url && (
                    
                    <a  href={profile.website_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-sm text-text-body hover:text-brand-primary transition-colors"
                    >
                      <Globe className="w-4 h-4 shrink-0" />
                      <span className="truncate">Website</span>
                    </a>
                  )}
                </div>

                {/* Skills */}
                {profile.skills?.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {profile.skills.map((skill) => (
                      <Badge key={skill} label={skill} variant="tag" />
                    ))}
                  </div>
                )}

                {/* Stats */}
                <div className="grid grid-cols-2 gap-3 pt-2 border-t border-ui-border">
                  <div className="text-center">
                    <p className="text-xl font-bold text-text-primary">{projects.length}</p>
                    <p className="text-xs text-text-muted">Projects</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-bold text-text-primary">
                      {projects.filter((p) => p.stage === 'completed').length}
                    </p>
                    <p className="text-xs text-text-muted">Completed</p>
                  </div>
                </div>

                {/* Edit button */}
                {isOwnProfile && (
                  <Button
                    variant="secondary"
                    fullWidth
                    onClick={() => setEditing(true)}
                  >
                    <Pencil className="w-4 h-4" /> Edit profile
                  </Button>
                )}

                {/* Follow placeholder — non-own profile */}
                {!isOwnProfile && isAuthenticated && (
                  <Button variant="ghost" fullWidth disabled>
                    <Users className="w-4 h-4" />
                    Follow (coming soon)
                  </Button>
                )}
                </>
            )}

            {/* ── Edit mode ── */}
            {editing && (
              <form
                onSubmit={handleSubmit(onSave)}
                noValidate
                className="flex flex-col gap-4"
              >
                <Input
                  label="Display name"
                  required
                  error={errors.display_name?.message}
                  {...register('display_name', {
                    required:  'Display name is required',
                    minLength: { value: 2,   message: 'At least 2 characters' },
                    maxLength: { value: 100, message: 'Max 100 characters' },
                  })}
                />

                <Textarea
                  label="Bio"
                  rows={3}
                  placeholder="Tell the community about yourself..."
                  {...register('bio', {
                    maxLength: { value: 500, message: 'Max 500 characters' },
                  })}
                />

                <Input
                  label="GitHub URL"
                  type="url"
                  placeholder="https://github.com/you"
                  error={errors.github_url?.message}
                  {...register('github_url', {
                    pattern: {
                      value:   /^https?:\/\/.+/,
                      message: 'Must be a valid URL',
                    },
                  })}
                />

                <Input
                  label="Website URL"
                  type="url"
                  placeholder="https://yoursite.com"
                  error={errors.website_url?.message}
                  {...register('website_url', {
                    pattern: {
                      value:   /^https?:\/\/.+/,
                      message: 'Must be a valid URL',
                    },
                  })}
                />

                <div className="flex flex-col gap-1">
                  <label className="text-sm font-medium text-text-primary">Skills</label>
                  <SkillsInput value={skills} onChange={setSkills} />
                </div>

                <div className="flex gap-2 pt-2">
                  <Button
                    type="button"
                    variant="ghost"
                    fullWidth
                    onClick={() => {
                      setEditing(false)
                      setSkills(profile.skills ?? [])
                      reset({
                        display_name: profile.display_name,
                        bio:          profile.bio          ?? '',
                        github_url:   profile.github_url   ?? '',
                        website_url:  profile.website_url  ?? '',
                      })
                    }}
                    disabled={savingProfile}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    fullWidth
                    loading={savingProfile}
                  >
                    Save
                  </Button>
                </div>
              </form>
            )}

          </div>
        </div>

        {/* ── Right column — projects + collab requests ── */}
        <div className="lg:col-span-2 flex flex-col gap-8">

          {/* Pending collab requests — own profile only */}
          {isOwnProfile && collabReqs.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Clock className="w-5 h-5 text-brand-primary" />
                <h2 className="text-lg font-semibold text-text-primary">
                  Collaboration requests
                </h2>
                <span className="px-2 py-0.5 text-xs font-bold bg-brand-primary text-white rounded-full">
                  {collabReqs.length}
                </span>
              </div>

              <div className="flex flex-col gap-3">
                {collabReqs.map((req) => (
                  <CollabRequestCard
                    key={req.id}
                    request={req}
                    onRespond={handleCollabRespond}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Projects */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <FolderOpen className="w-5 h-5 text-brand-primary" />
              <h2 className="text-lg font-semibold text-text-primary">
                {isOwnProfile ? 'Your projects' : `${profile.display_name}'s projects`}
              </h2>
              <span className="text-sm text-text-muted">({projects.length})</span>
            </div>

            {projects.length === 0 ? (
              <EmptyState
                icon={FolderOpen}
                title="No projects yet"
                description={
                  isOwnProfile
                    ? "You haven't created any projects. Start building in public!"
                    : `${profile.display_name} hasn't shared any projects yet.`
                }
                action={
                  isOwnProfile && (
                    <Link to="/projects/new">
                      <Button>Create your first project</Button>
                    </Link>
                  )
                }
              />
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {projects.map((project) => (
                  <ProjectCard key={project.id} project={project} />
                ))}
              </div>
            )}
          </section>

        </div>
      </div>
    </div>
  )
}
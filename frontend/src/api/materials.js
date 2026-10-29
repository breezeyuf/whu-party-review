import { api, getBlob } from "./client"
export const retryParse = (id) => api.post(`/materials/${id}/retry-parse`)

function form(file, fields = {}) {
  const fd = new FormData()
  fd.append("file", file)
  Object.entries(fields).forEach(([k, v]) => {
    if (v != null && v !== "") fd.append(k, v)
  })
  return fd
}

export const listMaterials = (archiveId, params) => api.get(`/archives/${archiveId}/materials`, { params })

export const uploadMaterial = (archiveId, file, fields = {}, onProgress) =>
  api.post(`/archives/${archiveId}/materials`, form(file, fields), {
    onUploadProgress: (e) => onProgress && onProgress(e.total ? Math.round((e.loaded / e.total) * 100) : 0),
  })

export const batchUpload = (file, fields = {}, onProgress) =>
  api.post("/materials/batch-upload", form(file, fields), {
    timeout: 0,
    onUploadProgress: (e) => onProgress && onProgress(e.total ? Math.round((e.loaded / e.total) * 100) : 0),
  })

export const assignBatch = (jobId, body) => api.put(`/materials/batch-upload/${jobId}/assign`, body)
export const getMaterial = (id) => api.get(`/materials/${id}`)
export const deleteMaterial = (id) => api.delete(`/materials/${id}`)
export const materialFile = (id, params) => getBlob(`/materials/${id}/file`, params)
export const materialPage = (id, n, params) => getBlob(`/materials/${id}/pages/${n}`, params)

export const uploadVersion = (id, file, fields = {}) => api.post(`/materials/${id}/versions`, form(file, fields))
export const listVersions = (id) => api.get(`/materials/${id}/versions`)
export const getParsed = (id, params) => api.get(`/materials/${id}/parsed`, { params })
export const putParsed = (id, body) => api.put(`/materials/${id}/parsed`, body)
export const setType = (id, materialTypeId) => api.put(`/materials/${id}/type`, { material_type_id: materialTypeId })
export const getDiff = (id, params) => api.get(`/materials/${id}/diff`, { params })

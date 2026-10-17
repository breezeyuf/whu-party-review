import { api } from "./client"

export function getMeta() {
  return api.get("/meta")
}

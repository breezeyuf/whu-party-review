import React, { act, StrictMode, useState } from "react"
import assert from "node:assert/strict"
import { createRoot } from "react-dom/client"
import { Modal, ModalLoading, ConfirmDialog } from "../src/components/common/Modal"
import AddIssueModal from "../src/components/review/AddIssueModal"

// JSDOM 缺少 dialog 的原生方法和 Escape 默认行为。只在 UI 测试期间补齐并还原；
// 不模拟浏览器的 inert/Tab 焦点约束，以免把模拟器行为误当作浏览器验证。
export async function withDialogPolyfill(run) {
  const prototype = window.HTMLDialogElement.prototype
  if (typeof prototype.showModal === "function" && typeof prototype.close === "function") return run()
  const descriptors = new Map(["showModal", "close"].map((name) => [name, Object.getOwnPropertyDescriptor(prototype, name)]))
  const stack = []
  const openers = new WeakMap()
  Object.defineProperty(prototype, "showModal", { configurable: true, writable: true, value() {
    if (this.open) return
    openers.set(this, document.activeElement)
    this.open = true
    stack.push(this)
    const focusable = this.querySelector('[autofocus], button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), a[href], [tabindex="0"]')
    focusable?.focus()
  } })
  Object.defineProperty(prototype, "close", { configurable: true, writable: true, value() {
    if (!this.open) return
    this.open = false
    const index = stack.indexOf(this)
    if (index !== -1) stack.splice(index, 1)
    const opener = openers.get(this)
    if (opener?.isConnected) opener.focus()
    queueMicrotask(() => this.dispatchEvent(new Event("close")))
  } })
  const escape = (event) => {
    if (event.key !== "Escape" || event.defaultPrevented) return
    const dialog = stack.findLast((node) => node.isConnected && node.open)
    if (dialog && dialog.dispatchEvent(new Event("cancel", { cancelable: true }))) dialog.close()
  }
  window.addEventListener("keydown", escape)
  try { return await run() }
  finally {
    window.removeEventListener("keydown", escape)
    for (const [name, descriptor] of descriptors) {
      if (descriptor) Object.defineProperty(prototype, name, descriptor)
      else delete prototype[name]
    }
  }
}

export async function runModalScenarios() {
  return withDialogPolyfill(async () => {
    const results = []
    let root, host
    const render = async (element) => {
      if (!root) {
        host = document.createElement("div")
        document.body.append(host)
        root = createRoot(host)
      }
      await act(async () => root.render(element))
    }
    const click = async (node) => {
      assert.ok(node, "未找到按钮")
      await act(async () => { node.focus(); node.click() })
    }
    const escape = async () => act(async () => {
      document.activeElement.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true, cancelable: true }))
    })
    const cleanup = async () => {
      if (root) await act(async () => root.unmount())
      root = null
      host?.remove()
      host = null
    }
    const test = async (name, run) => {
      try { await run(); results.push({ name, passed: true }) }
      catch (error) { results.push({ name, passed: false, error: error.stack || error.message }) }
      finally { await cleanup() }
    }

    await test("弹窗仅在打开时进入原生模态，普通重渲染保留输入焦点", async () => {
      let calls = 0
      const prototype = window.HTMLDialogElement.prototype
      const showModal = prototype.showModal
      prototype.showModal = function () { calls++; return showModal.call(this) }
      try {
        const view = (title) => <><button data-testid="opener">入口</button><Modal open title={title} onClose={() => {}}><input aria-label="弹窗输入" /></Modal></>
        await render(view("预览"))
        const dialog = host.querySelector("dialog")
        const input = host.querySelector("input")
        assert.equal(dialog.open, true)
        assert.equal(dialog.classList.contains("modal-open"), false)
        assert.equal(dialog.getAttribute("aria-labelledby"), host.querySelector("h3").id)
        input.focus()
        input.value = "未保存内容"
        await render(view("更新后的标题"))
        assert.equal(calls, 1)
        assert.equal(document.activeElement, input)
        assert.equal(input.value, "未保存内容")
      } finally { prototype.showModal = showModal }
    })

    await test("原生取消与遮罩关闭同步受控状态并恢复入口焦点", async () => {
      let requests = 0
      function Harness() {
        const [open, setOpen] = useState(false)
        return <><button data-testid="opener" onClick={() => setOpen(true)}>打开</button><Modal open={open} title="预览" onClose={() => { requests++; setOpen(false) }}><input /></Modal></>
      }
      await render(<Harness />)
      const opener = host.querySelector('[data-testid="opener"]')
      await click(opener)
      await escape()
      assert.equal(host.querySelector("dialog"), null)
      assert.equal(requests, 1)
      assert.equal(document.activeElement, opener)
      await click(opener)
      await click(host.querySelector(".modal-backdrop button"))
      assert.equal(host.querySelector("dialog"), null)
      assert.equal(requests, 2)
      assert.equal(document.activeElement, opener)
    })

    await test("busy 页面关闭守卫继续阻止 Escape、遮罩和取消，解除后可关闭", async () => {
      let requests = 0
      function Harness() {
        const [open, setOpen] = useState(false)
        const [busy, setBusy] = useState(true)
        return <><button data-testid="opener" onClick={() => setOpen(true)}>删除</button><ConfirmDialog open={open} title="删除材料" message="确认删除？" busy={busy} onConfirm={() => { throw new Error("测试不得写入业务数据") }} onClose={() => { requests++; if (!busy) setOpen(false) }} /><button data-testid="finish" onClick={() => setBusy(false)}>完成请求</button></>
      }
      await render(<Harness />)
      const opener = host.querySelector('[data-testid="opener"]')
      await click(opener)
      const dialog = host.querySelector("dialog")
      assert.equal(dialog.querySelector(".btn-error, .btn-primary").disabled, true)
      await escape()
      await click(dialog.querySelector(".modal-backdrop button"))
      await click([...dialog.querySelectorAll("button")].find((button) => button.textContent === "取消"))
      assert.equal(requests, 3)
      assert.equal(dialog.open, true)
      await click(host.querySelector('[data-testid="finish"]'))
      dialog.querySelector("button").focus()
      await escape()
      assert.equal(host.querySelector("dialog"), null)
      assert.equal(document.activeElement, opener)
    })

    await test("嵌套弹窗 Escape 仅关闭顶层，依次恢复父弹窗和页面入口", async () => {
      const closed = []
      function Harness() {
        const [parent, setParent] = useState(false), [child, setChild] = useState(false)
        return <><button data-testid="opener" onClick={() => setParent(true)}>材料预览</button><Modal open={parent} title="预览" onClose={() => { closed.push("parent"); setParent(false) }}><button data-testid="delete" onClick={() => setChild(true)}>删除文件</button><ConfirmDialog open={child} title="删除确认" message="确认？" onClose={() => { closed.push("child"); setChild(false) }} onConfirm={() => {}} /></Modal></>
      }
      await render(<Harness />)
      const opener = host.querySelector('[data-testid="opener"]')
      await click(opener)
      const parent = host.querySelector("dialog"), deletion = host.querySelector('[data-testid="delete"]')
      await click(deletion)
      assert.equal(host.querySelectorAll("dialog[open]").length, 2)
      await escape()
      assert.deepEqual(closed, ["child"])
      assert.equal(parent.open, true)
      assert.equal(document.activeElement, deletion)
      await escape()
      assert.deepEqual(closed, ["child", "parent"])
      assert.equal(host.querySelectorAll("dialog").length, 0)
      assert.equal(document.activeElement, opener)
    })

    await test("学生页面同级预览与删除确认保持父弹窗打开，确认操作只执行一次", async () => {
      let confirmed = 0
      function Harness() {
        const [preview, setPreview] = useState(false), [pending, setPending] = useState(false)
        return <><button data-testid="opener" onClick={() => setPreview(true)}>打开材料</button><Modal open={preview} title="材料" onClose={() => setPreview(false)} wide footer={<button data-testid="delete" onClick={() => setPending(true)}>删除</button>}>原件</Modal><ConfirmDialog open={pending} title="确认删除" message="确认？" danger confirmText="确认删除" onClose={() => setPending(false)} onConfirm={() => { confirmed++; setPending(false) }} /></>
      }
      await render(<Harness />)
      await click(host.querySelector('[data-testid="opener"]'))
      const deletion = host.querySelector('[data-testid="delete"]')
      await click(deletion)
      const dialogs = host.querySelectorAll("dialog")
      assert.equal(dialogs.length, 2)
      assert.ok(dialogs[0].querySelector(".max-w-3xl"))
      await click(dialogs[1].querySelector(".btn-error"))
      assert.equal(confirmed, 1)
      assert.equal(host.querySelectorAll("dialog[open]").length, 1)
      assert.equal(document.activeElement, deletion)
    })

    await test("外部原生 close 同步页面状态且不误关闭父弹窗", async () => {
      const closed = []
      function Harness() {
        const [child, setChild] = useState(false)
        return <Modal open title="父弹窗" onClose={() => closed.push("parent")}><button onClick={() => setChild(true)}>打开子弹窗</button><Modal open={child} title="子弹窗" onClose={() => { closed.push("child"); setChild(false) }}>内容</Modal></Modal>
      }
      await render(<Harness />)
      await click(host.querySelector("button"))
      await act(async () => host.querySelectorAll("dialog")[1].close())
      assert.deepEqual(closed, ["child"])
      assert.equal(host.querySelectorAll("dialog[open]").length, 1)
    })

    await test("父组件设为关闭和直接卸载均恢复仍存在的入口焦点", async () => {
      const opener = document.createElement("button")
      document.body.append(opener)
      try {
        opener.focus()
        await render(<Modal open title="预览" onClose={() => {}}><input /></Modal>)
        await render(<Modal open={false} title="预览" onClose={() => {}} />)
        assert.equal(document.activeElement, opener)
        await render(<Modal open title="预览" onClose={() => {}}><input /></Modal>)
        await cleanup()
        assert.equal(document.activeElement, opener)
      } finally { opener.remove() }
    })

    await test("StrictMode 重放不会被滞后的原生 close 事件误关闭", async () => {
      let requests = 0
      await render(<StrictMode><Modal open title="预览" onClose={() => requests++}><input /></Modal></StrictMode>)
      assert.equal(host.querySelector("dialog").open, true)
      assert.equal(requests, 0)
    })

    await test("加载占位也使用原生模态并在卸载后恢复入口", async () => {
      const opener = document.createElement("button")
      document.body.append(opener)
      try {
        opener.focus()
        await render(<ModalLoading />)
        const dialog = host.querySelector("dialog")
        assert.equal(dialog.open, true)
        assert.equal(dialog.getAttribute("aria-busy"), "true")
        await escape()
        assert.equal(dialog.open, true)
        await cleanup()
        assert.equal(document.activeElement, opener)
      } finally { opener.remove() }
    })

    await test("嵌套加载占位的 Escape 不会触发父弹窗关闭", async () => {
      let closed = 0
      function Harness() {
        const [loading, setLoading] = useState(false)
        return <Modal open title="父弹窗" onClose={() => closed++}><button onClick={() => setLoading(true)}>加载子弹窗</button>{loading && <ModalLoading />}</Modal>
      }
      await render(<Harness />)
      await click(host.querySelector("button"))
      await escape()
      assert.equal(closed, 0)
      assert.equal(host.querySelectorAll("dialog[open]").length, 2)
    })

    await test("现有人工新增问题调用保留取消行为和入口焦点", async () => {
      function Harness() {
        const [open, setOpen] = useState(false)
        return <><button data-testid="opener" onClick={() => setOpen(true)}>新增问题</button><AddIssueModal open={open} onClose={() => setOpen(false)} onCreate={() => { throw new Error("测试不得写入业务数据") }} /></>
      }
      await render(<Harness />)
      const opener = host.querySelector('[data-testid="opener"]')
      await click(opener)
      assert.equal(host.querySelector("dialog").open, true)
      assert.equal(host.querySelector("h3").textContent, "人工新增问题")
      await click([...host.querySelectorAll("button")].find((button) => button.textContent === "取消"))
      assert.equal(host.querySelector("dialog"), null)
      assert.equal(document.activeElement, opener)
    })

    return results
  })
}

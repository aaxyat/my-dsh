/**
 * Client half of the pinned-workspaces bundle.
 *
 * Adds three contributions to the Web page:
 *  - a Pin/Unpin action in the Workspace context menu (right-click and the
 *    row's "..." menu share it);
 *  - a sidebar-foot toggle that opens the pinned quick-access list;
 *  - the floating "Pinned workspaces" panel itself.
 *
 * Pinning also moves the Workspace to the front of the sidebar list, the same
 * way a pinned Session leads its row order. The pin set lives in this browser,
 * next to the sidebar's own persisted view state.
 */
window.__ModuleLoader__.load({
  id: '@local/pinned-workspaces',
  factory(require) {
    const React = require('react')
    const h = React.createElement

    /** Locale namespace owned by this plugin. */
    const NS = 'pinnedWorkspaces'
    /** Browser store key for the pinned Workspace ids. */
    const STORAGE_KEY = 'dsh.pinned.workspaces.v1'
    /** Stored title of the automatic first-use Workspace, which is shown localized. */
    const DEFAULT_WORKSPACE_TITLE = 'default-workspace'
    /** Marks the sidebar-foot toggle so the panel skips its own dismissal click. */
    const TOGGLE_ATTRIBUTE = 'data-pinned-workspaces-toggle'
    /** The Workspace target family published by ui-context-menu. */
    const WORKSPACE_TARGET = 'workspace'

    /** Pinned list labels; English is the key-set source of truth. */
    const en = {
      'button.label': 'Pinned workspaces',
      'panel.close': 'Close pinned workspaces',
      'panel.empty': 'No pinned workspaces yet.',
      'panel.hint': 'Right-click a workspace in the sidebar, or open its "..." menu, then choose Pin workspace.',
      'panel.loading': 'Loading workspaces…',
      'defaultName': 'Default workspace',
      'menu.pin': 'Pin workspace',
      'menu.unpin': 'Unpin workspace',
      'row.unpin': 'Unpin {name}',
      'toast.reorderFailed': 'Pinned, but the workspace could not be moved to the top.',
      'toast.openFailed': 'Could not open that workspace.',
    }

    /** Simplified Chinese dictionary. */
    const zh = {
      'button.label': '已固定工作区',
      'panel.close': '关闭已固定工作区',
      'panel.empty': '还没有固定的工作区。',
      'panel.hint': '在侧边栏右键工作区或打开“...”菜单，然后选择“固定工作区”。',
      'panel.loading': '正在加载工作区…',
      'defaultName': '默认工作区',
      'menu.pin': '固定工作区',
      'menu.unpin': '取消固定工作区',
      'row.unpin': '取消固定 {name}',
      'toast.reorderFailed': '已固定，但无法将该工作区移到顶部。',
      'toast.openFailed': '无法打开该工作区。',
    }

    /**
     * Read the stored pin set.
     * @returns pinned Workspace ids in pin order, newest first.
     */
    function readPinnedIds() {
      try {
        const raw = window.localStorage.getItem(STORAGE_KEY)
        if (raw === null) return []
        const value = JSON.parse(raw)
        return Array.isArray(value) ? value.filter((id) => typeof id === 'string') : []
      } catch (error) {
        console.error('pinned-workspaces: cannot read the stored pins', error)
        return []
      }
    }

    /** @param ids - complete pin set; failures are reported, never thrown. */
    function writePinnedIds(ids) {
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(ids))
      } catch (error) {
        console.error('pinned-workspaces: cannot store the pins', error)
      }
    }

    /** @returns whether both sequences carry the same ids in the same order. */
    function sameIds(left, right) {
      return left.length === right.length && left.every((id, index) => id === right[index])
    }

    /**
     * Browser-backed pin set. The snapshot keeps its identity until the set
     * changes, so subscribers and the context-menu registry re-resolve only on
     * a real pin or unpin.
     * @returns the observable set and its mutations.
     */
    function createPinStore() {
      let ids = readPinnedIds()
      const listeners = new Set()
      const publish = () => {
        for (const listener of [...listeners]) {
          try {
            listener()
          } catch (error) {
            console.error('pinned-workspaces: pin listener failed', error)
          }
        }
      }
      const commit = (next) => {
        if (sameIds(ids, next)) return false
        ids = next
        writePinnedIds(ids)
        publish()
        return true
      }
      return {
        getSnapshot: () => ids,
        subscribe(listener) {
          listeners.add(listener)
          return () => {
            listeners.delete(listener)
          }
        },
        has: (workspaceId) => ids.includes(workspaceId),
        pin: (workspaceId) => commit([workspaceId, ...ids.filter((id) => id !== workspaceId)]),
        unpin: (workspaceId) => commit(ids.filter((id) => id !== workspaceId)),
        prune: (retained) => commit(ids.filter((id) => retained.has(id))),
      }
    }

    /**
     * In-memory boolean with the same observable shape as the pin store.
     * @param initial - starting value.
     * @returns the observable flag and its mutations.
     */
    function createFlagStore(initial) {
      let value = initial
      const listeners = new Set()
      const set = (next) => {
        if (value === next) return
        value = next
        for (const listener of [...listeners]) listener()
      }
      return {
        getSnapshot: () => value,
        subscribe(listener) {
          listeners.add(listener)
          return () => {
            listeners.delete(listener)
          }
        },
        set,
        toggle: () => set(!value),
      }
    }

    /**
     * Subscribe one component to an observable snapshot.
     * @param store - source with `getSnapshot` and `subscribe`.
     * @returns the current snapshot.
     */
    function useSnapshot(store) {
      const [snapshot, setSnapshot] = React.useState(() => store.getSnapshot())
      React.useEffect(() => {
        const sync = () => setSnapshot(store.getSnapshot())
        sync()
        return store.subscribe(sync)
      }, [store])
      return snapshot
    }

    /** Original thumbtack outline glyph; inherits `currentColor`. */
    function PinGlyph({ filled = false, className }) {
      return h(
        'svg',
        {
          className,
          viewBox: '0 0 16 16',
          width: 16,
          height: 16,
          fill: filled ? 'currentColor' : 'none',
          stroke: 'currentColor',
          strokeWidth: filled ? 0.6 : 1.2,
          strokeLinejoin: 'round',
          strokeLinecap: 'round',
          'aria-hidden': true,
          focusable: false,
        },
        h('path', { d: 'M6.2 2.3h3.6l-.4 3.2 1.9 2.1v1.2H4.7V7.6l1.9-2.1-.4-3.2Z' }),
        h('path', { d: 'M8 8.8v4.4', fill: 'none', strokeWidth: 1.2 }),
      )
    }

    /** Original close glyph; inherits `currentColor`. */
    function CloseGlyph({ className }) {
      return h(
        'svg',
        {
          className,
          viewBox: '0 0 16 16',
          width: 16,
          height: 16,
          fill: 'none',
          stroke: 'currentColor',
          strokeWidth: 1.3,
          strokeLinecap: 'round',
          'aria-hidden': true,
          focusable: false,
        },
        h('path', { d: 'M4.4 4.4l7.2 7.2M11.6 4.4l-7.2 7.2' }),
      )
    }

    /** Plugin-owned rules; only theme tokens and sidebar variables are referenced. */
    const css = `
.pw-foot{box-sizing:border-box;display:flex;flex:none;width:100%;min-width:0;margin:0 0 2px;padding:0}
.pw-foot-rail{width:auto;justify-content:center}
.pw-foot-button{display:flex;align-items:center;gap:var(--dsh-sidebar-label-gap,6px);box-sizing:border-box;width:100%;height:34px;margin:0;padding:0 calc(var(--dsh-sidebar-row-padding,12px) - var(--dsh-sidebar-paint-inset,3px));border:0;border-inline:var(--dsh-sidebar-paint-inset,3px) solid transparent;border-radius:var(--dsw-radius-md,8px);background:transparent;background-clip:padding-box;color:var(--dsw-alias-label-primary);font-family:inherit;font-size:14px;line-height:22px;text-align:left;cursor:pointer;overflow:hidden}
.pw-foot-button:hover{background-color:var(--dsw-alias-interactive-bg-hover,rgba(128,128,128,.14))}
.pw-foot-button:focus-visible{outline:2px solid var(--dsw-alias-brand-primary);outline-offset:-2px}
.pw-foot-button-rail{width:36px;height:36px;justify-content:center;gap:0;padding:0;border-inline:0;background-clip:border-box}
.pw-foot-icon{flex:none;color:var(--dsw-alias-label-secondary)}
.pw-foot-button:hover .pw-foot-icon,.pw-foot-button[aria-expanded=true] .pw-foot-icon{color:var(--dsw-alias-label-primary)}
.pw-foot-label{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pw-foot-count{flex:none;min-width:16px;height:16px;padding:0 4px;box-sizing:border-box;border-radius:8px;background:var(--dsw-alias-brand-primary);color:var(--dsw-alias-bg-base);font-size:10px;line-height:16px;font-weight:600;text-align:center}
.pw-panel{position:fixed;left:12px;bottom:96px;z-index:40;box-sizing:border-box;display:flex;flex-direction:column;width:min(320px,calc(100vw - 24px));max-height:min(60vh,440px);padding:6px;border:0.5px solid var(--dsw-alias-border-l1);border-radius:12px;background:var(--dsw-alias-bg-overlay);color:var(--dsw-alias-label-primary);box-shadow:0 10px 30px rgba(0,0,0,.22);font-size:13px;line-height:18px;outline:none}
.pw-panel-head{display:flex;align-items:center;gap:8px;flex:none;padding:4px 4px 6px 8px}
.pw-panel-head-icon{flex:none;color:var(--dsw-alias-label-secondary)}
.pw-panel-title{flex:1;min-width:0;margin:0;font-size:13px;font-weight:500;line-height:20px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pw-icon-button{display:inline-flex;align-items:center;justify-content:center;flex:none;width:26px;height:26px;margin:0;padding:0;border:0;border-radius:6px;background:transparent;color:var(--dsw-alias-label-secondary);cursor:pointer}
.pw-icon-button:hover{background-color:var(--dsw-alias-interactive-bg-hover,rgba(128,128,128,.14));color:var(--dsw-alias-label-primary)}
.pw-icon-button:focus-visible{outline:2px solid var(--dsw-alias-brand-primary);outline-offset:-2px}
.pw-list{display:flex;flex-direction:column;gap:2px;min-height:0;margin:0;padding:0;list-style:none;overflow-y:auto}
.pw-row{display:flex;align-items:center;gap:2px;border-radius:8px}
.pw-row:hover{background-color:var(--dsw-alias-interactive-bg-hover,rgba(128,128,128,.14))}
.pw-row-open{display:flex;align-items:center;gap:8px;flex:1;min-width:0;margin:0;padding:6px 6px 6px 8px;border:0;border-radius:8px;background:transparent;color:inherit;font:inherit;text-align:left;cursor:pointer}
.pw-row-open:focus-visible{outline:2px solid var(--dsw-alias-brand-primary);outline-offset:-2px}
.pw-row-pin{flex:none;color:var(--dsw-alias-brand-primary)}
.pw-row-text{display:flex;flex-direction:column;min-width:0}
.pw-row-title{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--dsw-alias-label-primary)}
.pw-row-path{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--dsw-alias-label-secondary);font-size:11px;line-height:15px}
.pw-empty{margin:0;padding:6px 8px 10px;color:var(--dsw-alias-label-secondary);font-size:12px;line-height:18px}
`

    /**
     * One client plugin: pin action, sidebar-foot toggle, and quick-access panel.
     * @param ctx - Client plugin context with the injected Workspace, menu, slot, and locale services.
     */
    function apply(ctx) {
      const t = ctx.locale.bind(NS)
      const pinStore = createPinStore()
      const panelStore = createFlagStore(false)
      const workspaceList = ctx.workspaces.list

      ctx.effect(() => ctx.locale.register(NS, { en, zh }), 'pinned-workspaces: locale')

      /** Drop pins for Workspaces this profile no longer has, once a baseline is in. */
      ctx.effect(() => {
        const prune = () => {
          const snapshot = workspaceList.getSnapshot()
          if (snapshot.state !== 'idle' || snapshot.items.length === 0) return
          pinStore.prune(new Set(snapshot.items.map((workspace) => workspace.workspaceId)))
        }
        prune()
        return workspaceList.subscribe(prune)
      }, 'pinned-workspaces: prune removed workspaces')

      /**
       * Move one Workspace to the front of the saved order. The pin stands even
       * when the Host refuses the reorder, so the quick-access list still works.
       * @param workspaceId - Workspace whose pin was just added.
       */
      const moveToFront = async (workspaceId) => {
        const workspaces = ctx.get('workspaces')
        if (workspaces === undefined) return
        const order = workspaceList.getSnapshot().items.map((workspace) => workspace.workspaceId)
        if (order.indexOf(workspaceId) <= 0) return
        try {
          await workspaces.insertBefore(workspaceId, order[0])
        } catch (error) {
          console.error('pinned-workspaces: cannot move the workspace to the front', error)
          ctx.contextMenus.notify(t('toast.reorderFailed'), false)
        }
      }

      const setPinned = (workspaceId, pinned) => {
        const changed = pinned ? pinStore.pin(workspaceId) : pinStore.unpin(workspaceId)
        if (changed && pinned) void moveToFront(workspaceId)
      }

      const openWorkspace = (workspaceId) => {
        const navigation = ctx.get('uiWorkspace')
        if (navigation === undefined) {
          ctx.contextMenus.notify(t('toast.openFailed'), false)
          return
        }
        panelStore.set(false)
        Promise.resolve(navigation.openWorkspace(workspaceId)).catch((error) => {
          console.error('pinned-workspaces: cannot open the workspace', error)
          ctx.contextMenus.notify(t('toast.openFailed'), false)
        })
      }

      /** @returns one localized Workspace label, defaulting the automatic title. */
      const workspaceTitle = (workspace) =>
        workspace.title === DEFAULT_WORKSPACE_TITLE ? t('defaultName') : workspace.title

      /** Sidebar-foot toggle: always present, opens and closes the pinned list. */
      function PinnedFooterAction(props) {
        const pinnedIds = useSnapshot(pinStore)
        const open = useSnapshot(panelStore)
        const wide = props.wide !== false
        const label = props.t('button.label')
        return h(
          React.Fragment,
          null,
          h('style', null, css),
          h(
            'div',
            { className: wide ? 'pw-foot' : 'pw-foot pw-foot-rail' },
            h(
              'button',
              {
                type: 'button',
                className: wide ? 'pw-foot-button' : 'pw-foot-button pw-foot-button-rail',
                'aria-label': label,
                title: label,
                'aria-haspopup': 'dialog',
                'aria-expanded': open,
                [TOGGLE_ATTRIBUTE]: '',
                onClick: () => props.togglePanel(),
              },
              h(PinGlyph, { className: 'pw-foot-icon', filled: pinnedIds.length > 0 }),
              wide ? h('span', { className: 'pw-foot-label' }, label) : null,
              wide && pinnedIds.length > 0
                ? h('span', { className: 'pw-foot-count' }, String(pinnedIds.length))
                : null,
            ),
          ),
        )
      }

      /** The pinned quick-access list, rendered in the frame overlay. */
      function PinnedPanel(props) {
        const open = useSnapshot(panelStore)
        const pinnedIds = useSnapshot(pinStore)
        const workspaces = useSnapshot(workspaceList)
        const panelRef = React.useRef(null)

        React.useEffect(() => {
          if (!open) return undefined
          /** Dismissal that leaves the keyboard where the gesture started. */
          const closeAndRestoreFocus = () => {
            props.closePanel()
            const toggle = document.querySelector('[' + TOGGLE_ATTRIBUTE + ']')
            if (toggle instanceof HTMLElement) toggle.focus()
          }
          const onKeyDown = (event) => {
            if (event.key !== 'Escape') return
            event.preventDefault()
            closeAndRestoreFocus()
          }
          const onPointerDown = (event) => {
            const panel = panelRef.current
            const target = event.target
            if (panel === null || !(target instanceof Node) || panel.contains(target)) return
            if (target instanceof Element && target.closest('[' + TOGGLE_ATTRIBUTE + ']') !== null) return
            closeAndRestoreFocus()
          }
          document.addEventListener('keydown', onKeyDown, true)
          document.addEventListener('pointerdown', onPointerDown, true)
          return () => {
            document.removeEventListener('keydown', onKeyDown, true)
            document.removeEventListener('pointerdown', onPointerDown, true)
          }
          // The injected actions close over one plugin instance, so their
          // identity per render does not change what the listeners do.
          // eslint-disable-next-line react-hooks/exhaustive-deps
        }, [open])

        React.useEffect(() => {
          if (open && panelRef.current !== null) panelRef.current.focus()
        }, [open])

        if (!open) return null

        const byId = new Map(workspaces.items.map((workspace) => [workspace.workspaceId, workspace]))
        const rows = pinnedIds.map((id) => byId.get(id)).filter((workspace) => workspace !== undefined)
        const body =
          rows.length > 0
            ? h(
                'ul',
                { className: 'pw-list' },
                rows.map((workspace) =>
                  h(
                    'li',
                    { key: workspace.workspaceId, className: 'pw-row' },
                    h(
                      'button',
                      {
                        type: 'button',
                        className: 'pw-row-open',
                        title: workspace.path,
                        onClick: () => props.openPinnedWorkspace(workspace.workspaceId),
                      },
                      h(PinGlyph, { className: 'pw-row-pin', filled: true }),
                      h(
                        'span',
                        { className: 'pw-row-text' },
                        h('span', { className: 'pw-row-title' }, workspaceTitle(workspace)),
                        h('span', { className: 'pw-row-path' }, workspace.path),
                      ),
                    ),
                    h(
                      'button',
                      {
                        type: 'button',
                        className: 'pw-icon-button',
                        'aria-label': props.t('row.unpin', { name: workspaceTitle(workspace) }),
                        title: props.t('row.unpin', { name: workspaceTitle(workspace) }),
                        onClick: () => props.unpinPinnedWorkspace(workspace.workspaceId),
                      },
                      h(CloseGlyph, null),
                    ),
                  ),
                ),
              )
            : h(
                'p',
                { className: 'pw-empty' },
                props.t(pinnedIds.length > 0 ? 'panel.loading' : 'panel.empty'),
                pinnedIds.length > 0 ? null : h('br', null),
                pinnedIds.length > 0 ? null : props.t('panel.hint'),
              )

        return h(
          React.Fragment,
          null,
          h('style', null, css),
          h(
            'div',
            {
              className: 'pw-panel',
              role: 'dialog',
              'aria-label': props.t('panel.title'),
              tabIndex: -1,
              ref: panelRef,
            },
            h(
              'div',
              { className: 'pw-panel-head' },
              h(PinGlyph, { className: 'pw-panel-head-icon', filled: true }),
              h('h2', { className: 'pw-panel-title' }, props.t('panel.title')),
              h(
                'button',
                {
                  type: 'button',
                  className: 'pw-icon-button',
                  'aria-label': props.t('panel.close'),
                  title: props.t('panel.close'),
                  onClick: () => props.closePanel(),
                },
                h(CloseGlyph, null),
              ),
            ),
            body,
          ),
        )
      }

      ctx.effect(
        () =>
          ctx.contextMenus.register({
            id: 'pinnedWorkspaces.togglePin',
            target: WORKSPACE_TARGET,
            order: 50,
            observe: () => [pinStore, ctx.locale],
            resolve: ({ workspaceId }) => {
              const pinned = pinStore.has(workspaceId)
              return [
                {
                  id: 'toggle',
                  label: t(pinned ? 'menu.unpin' : 'menu.pin'),
                  icon: { key: pinned ? 'pinnedWorkspaces.unpin' : 'pinnedWorkspaces.pin' },
                  run: () => setPinned(workspaceId, !pinned),
                },
              ]
            },
          }),
        'pinned-workspaces: workspace menu action',
      )

      ctx.slots.inject('contextMenu.icon', () =>
        ctx.slots.register({ name: 'contextMenu.icon', key: 'pinnedWorkspaces.pin' }, (props) =>
          h(PinGlyph, { ...props, filled: false }),
        ),
      )
      ctx.slots.inject('contextMenu.icon', () =>
        ctx.slots.register({ name: 'contextMenu.icon', key: 'pinnedWorkspaces.unpin' }, (props) =>
          h(PinGlyph, { ...props, filled: true }),
        ),
      )

      ctx.slots.inject('sidebar.footer.action', () =>
        ctx.slots.register(
          {
            name: 'sidebar.footer.action',
            id: 'pinned-workspaces',
            order: 10,
            locale: NS,
            inject: () => ({ togglePanel: () => panelStore.toggle() }),
          },
          PinnedFooterAction,
        ),
      )

      ctx.slots.inject('shell.overlay', () =>
        ctx.slots.register(
          {
            name: 'shell.overlay',
            id: 'pinned-workspaces.panel',
            order: 40,
            locale: NS,
            inject: () => ({
              close: () => panelStore.set(false),
              openWorkspace,
              unpin: (workspaceId) => setPinned(workspaceId, false),
            }),
          },
          PinnedPanel,
        ),
      )
    }

    return {
      inject: ['slots', 'locale', 'workspaces', 'contextMenus'],
      apply,
    }
  },
})

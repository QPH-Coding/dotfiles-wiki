local M = {}

local keymaps = require("core.keymaps")
local map = keymaps.mapper("Terminal")
local augroup = vim.api.nvim_create_augroup("dotfiles_wiki_terminal", { clear = true })
local tabbar_namespace = vim.api.nvim_create_namespace("dotfiles_wiki_terminal_tabbar")
local tab_states = {}

local function state()
  local tabpage = vim.api.nvim_get_current_tabpage()
  local id = tostring(tabpage)

  if type(tab_states[id]) ~= "table" then
    tab_states[id] = {
      buffers = {},
      current = nil,
      last_workspace_winid = nil,
      suspend_redirect = false,
      tab_bufnr = nil,
      tab_spans = {},
      tab_winid = nil,
      term_winid = nil,
    }
  end

  return tab_states[id]
end

local function with_redirect_suspended(fn)
  local terminal_state = state()
  local previous = terminal_state.suspend_redirect
  terminal_state.suspend_redirect = true

  local ok, result = pcall(fn)

  terminal_state.suspend_redirect = previous

  if not ok then
    error(result)
  end

  return result
end

local function is_valid_win(winid)
  return type(winid) == "number" and vim.api.nvim_win_is_valid(winid)
end

local function is_valid_buf(bufnr)
  return type(bufnr) == "number" and vim.api.nvim_buf_is_valid(bufnr)
end

local function is_tabbar_window(winid)
  return is_valid_win(winid) and vim.w[winid].terminal_tabbar == true
end

local function is_terminal_window(winid)
  return is_valid_win(winid) and vim.w[winid].terminal_panel_terminal == true
end

local function is_panel_window(winid)
  return is_tabbar_window(winid) or is_terminal_window(winid)
end

local function is_workspace_window(winid)
  if not is_valid_win(winid) or is_panel_window(winid) then
    return false
  end

  return vim.api.nvim_win_get_config(winid).relative == ""
end

local function is_managed_terminal(bufnr)
  return is_valid_buf(bufnr) and vim.bo[bufnr].buftype == "terminal" and vim.b[bufnr].terminal_panel_managed == true
end

local function is_terminal_buffer(bufnr)
  return is_valid_buf(bufnr) and vim.bo[bufnr].buftype == "terminal"
end

local function is_tabbar_buffer(bufnr)
  return is_valid_buf(bufnr) and bufnr == state().tab_bufnr
end

local function cleanup_buffers()
  local terminal_state = state()
  local active = {}

  for _, bufnr in ipairs(terminal_state.buffers) do
    if is_managed_terminal(bufnr) then
      table.insert(active, bufnr)
    end
  end

  terminal_state.buffers = active

  if not is_managed_terminal(terminal_state.current) then
    terminal_state.current = active[#active]
  end
end

local function terminal_width()
  return math.max(42, math.floor(vim.o.columns * 0.4))
end

local function terminal_label(bufnr, index)
  local title = vim.trim(vim.b[bufnr].term_title or "")

  if title ~= "" then
    title = vim.fn.fnamemodify(title, ":t")
  end

  if title == "" then
    title = "term " .. index
  end

  return index .. ":" .. title
end

local function tabbar_item_at_cursor()
  local terminal_state = state()

  if not is_tabbar_window(terminal_state.tab_winid) then
    return nil
  end

  local column = vim.api.nvim_win_get_cursor(terminal_state.tab_winid)[2] + 1

  for _, span in ipairs(terminal_state.tab_spans) do
    if column >= span.start_col and column <= span.end_col then
      return span
    end
  end

  return nil
end

local function ensure_tabbar_buffer()
  local terminal_state = state()

  if is_valid_buf(terminal_state.tab_bufnr) then
    return terminal_state.tab_bufnr
  end

  local bufnr = vim.api.nvim_create_buf(false, true)
  terminal_state.tab_bufnr = bufnr

  vim.bo[bufnr].buftype = "nofile"
  vim.bo[bufnr].bufhidden = "hide"
  vim.bo[bufnr].swapfile = false
  vim.bo[bufnr].modifiable = false
  vim.bo[bufnr].buflisted = false
  vim.bo[bufnr].filetype = "terminal-tabs"

  vim.keymap.set("n", "<CR>", function()
    M.activate_tabbar_item()
  end, { buffer = bufnr, desc = "Activate terminal tab" })

  vim.keymap.set("n", "<LeftMouse>", function()
    M.activate_tabbar_item()
  end, { buffer = bufnr, desc = "Activate terminal tab" })

  return bufnr
end

local function update_tabbar()
  local terminal_state = state()
  local bufnr = ensure_tabbar_buffer()
  local text = {}
  local spans = {}
  local highlights = {}
  local column = 0

  cleanup_buffers()

  local function append(segment, hl_group, action)
    if segment == "" then
      return
    end

    table.insert(text, segment)
    table.insert(highlights, {
      group = hl_group,
      start_col = column,
      end_col = column + #segment,
    })

    if action then
      table.insert(spans, {
        action = action,
        start_col = column + 1,
        end_col = column + #segment,
      })
    end

    column = column + #segment
  end

  if #terminal_state.buffers == 0 then
    append(" no terminals ", "TabLineSel", { kind = "new" })
  else
    for index, bufnr_value in ipairs(terminal_state.buffers) do
      local is_current = bufnr_value == terminal_state.current
      local hl_group = is_current and "TabLineSel" or "TabLine"
      local left = is_current and "[" or " "
      local right = is_current and "]" or " "

      append(left .. terminal_label(bufnr_value, index) .. right, hl_group, {
        index = index,
        kind = "terminal",
      })
      append(" ", "TabLineFill")
    end
  end

  append(" + ", "TabLine", { kind = "new" })

  terminal_state.tab_spans = spans

  vim.bo[bufnr].modifiable = true
  vim.api.nvim_buf_set_lines(bufnr, 0, -1, false, { table.concat(text) })
  vim.bo[bufnr].modifiable = false

  vim.api.nvim_buf_clear_namespace(bufnr, tabbar_namespace, 0, -1)

  for _, item in ipairs(highlights) do
    vim.api.nvim_buf_add_highlight(bufnr, tabbar_namespace, item.group, 0, item.start_col, item.end_col)
  end
end

local function apply_tabbar_style(winid)
  local bufnr = ensure_tabbar_buffer()

  vim.w[winid].terminal_panel = true
  vim.w[winid].terminal_tabbar = true
  vim.w[winid].terminal_panel_terminal = false

  vim.api.nvim_win_set_buf(winid, bufnr)

  vim.wo[winid].number = false
  vim.wo[winid].relativenumber = false
  vim.wo[winid].signcolumn = "no"
  vim.wo[winid].cursorline = false
  vim.wo[winid].winfixheight = true
  vim.wo[winid].winfixwidth = true
  vim.wo[winid].winfixbuf = true
  vim.wo[winid].wrap = false
  vim.wo[winid].spell = false
  vim.wo[winid].list = false
  vim.wo[winid].winbar = ""

  vim.api.nvim_win_set_height(winid, 1)
  update_tabbar()
end

local function apply_terminal_style(winid)
  vim.w[winid].terminal_panel = true
  vim.w[winid].terminal_tabbar = false
  vim.w[winid].terminal_panel_terminal = true

  vim.wo[winid].number = false
  vim.wo[winid].relativenumber = false
  vim.wo[winid].signcolumn = "no"
  vim.wo[winid].cursorline = false
  vim.wo[winid].winfixwidth = true
  vim.wo[winid].winfixbuf = true
  vim.api.nvim_win_set_width(winid, terminal_width())
end

local function create_tabbar_above(term_winid)
  local terminal_state = state()

  vim.api.nvim_set_current_win(term_winid)
  vim.cmd("leftabove 1split")

  terminal_state.tab_winid = vim.api.nvim_get_current_win()
  apply_tabbar_style(terminal_state.tab_winid)
  apply_terminal_style(term_winid)
  vim.api.nvim_set_current_win(term_winid)
end

local function create_terminal_below(tab_winid)
  local terminal_state = state()

  vim.api.nvim_set_current_win(tab_winid)
  vim.cmd("rightbelow split")

  terminal_state.term_winid = vim.api.nvim_get_current_win()
  apply_tabbar_style(tab_winid)
  apply_terminal_style(terminal_state.term_winid)
  vim.api.nvim_set_current_win(terminal_state.term_winid)
end

local function create_panel()
  local terminal_state = state()

  vim.cmd("botright vsplit")

  terminal_state.term_winid = vim.api.nvim_get_current_win()
  create_tabbar_above(terminal_state.term_winid)

  return terminal_state.term_winid
end

local function ensure_panel()
  return with_redirect_suspended(function()
    local terminal_state = state()
    local tabbar_valid = is_tabbar_window(terminal_state.tab_winid)
    local terminal_valid = is_terminal_window(terminal_state.term_winid)

    if tabbar_valid and terminal_valid then
      apply_tabbar_style(terminal_state.tab_winid)
      apply_terminal_style(terminal_state.term_winid)
      return terminal_state.term_winid
    end

    if terminal_valid then
      create_tabbar_above(terminal_state.term_winid)
      return terminal_state.term_winid
    end

    if tabbar_valid then
      create_terminal_below(terminal_state.tab_winid)
      return terminal_state.term_winid
    end

    return create_panel()
  end)
end

local function set_terminal_buffer(bufnr, opts)
  opts = opts or {}

  local terminal_state = state()
  local winid = ensure_panel()

  terminal_state.current = bufnr

  vim.api.nvim_set_current_win(winid)
  vim.api.nvim_set_option_value("winfixbuf", false, { win = winid })
  vim.cmd("setlocal nowinfixbuf")
  vim.api.nvim_win_set_buf(winid, bufnr)
  apply_terminal_style(winid)
  update_tabbar()

  if opts.enter_insert ~= false then
    vim.cmd("startinsert")
  end
end

local function register_terminal(bufnr)
  local terminal_state = state()

  if not vim.tbl_contains(terminal_state.buffers, bufnr) then
    table.insert(terminal_state.buffers, bufnr)
  end

  terminal_state.current = bufnr

  vim.b[bufnr].terminal_panel_managed = true
  vim.bo[bufnr].buflisted = false
  vim.bo[bufnr].bufhidden = "hide"

  update_tabbar()
end

local function restore_tabbar()
  local terminal_state = state()

  if not is_tabbar_window(terminal_state.tab_winid) then
    return
  end

  apply_tabbar_style(terminal_state.tab_winid)
end

local function current_terminal_index()
  local terminal_state = state()
  cleanup_buffers()

  for index, bufnr in ipairs(terminal_state.buffers) do
    if bufnr == terminal_state.current then
      return index
    end
  end

  return #terminal_state.buffers > 0 and 1 or nil
end

local function record_workspace_window(winid)
  if is_workspace_window(winid) then
    state().last_workspace_winid = winid
  end
end

local function find_workspace_window()
  local terminal_state = state()

  if is_workspace_window(terminal_state.last_workspace_winid) then
    return terminal_state.last_workspace_winid
  end

  for _, winid in ipairs(vim.api.nvim_tabpage_list_wins(0)) do
    if is_workspace_window(winid) then
      terminal_state.last_workspace_winid = winid
      return winid
    end
  end

  return nil
end

local function create_terminal_buffer()
  local current_winid = vim.api.nvim_get_current_win()
  local float_bufnr = vim.api.nvim_create_buf(false, true)
  local float_winid = vim.api.nvim_open_win(float_bufnr, false, {
    relative = "editor",
    row = 0,
    col = 0,
    width = 1,
    height = 1,
    style = "minimal",
    focusable = false,
  })

  vim.api.nvim_set_current_win(float_winid)
  vim.cmd("terminal")

  local bufnr = vim.api.nvim_get_current_buf()

  if is_valid_win(current_winid) then
    vim.api.nvim_set_current_win(current_winid)
  end

  if is_valid_win(float_winid) then
    vim.api.nvim_win_close(float_winid, true)
  end

  return bufnr
end

function M.activate_tabbar_item()
  local item = tabbar_item_at_cursor()
  if not item then
    return
  end

  if item.action.kind == "new" then
    M.new()
    return
  end

  if item.action.kind == "terminal" then
    M.select(item.action.index)
  end
end

function M.select(index, opts)
  local terminal_state = state()
  cleanup_buffers()

  local bufnr = terminal_state.buffers[index]
  if not is_managed_terminal(bufnr) then
    return
  end

  set_terminal_buffer(bufnr, opts)
end

function M.open()
  local terminal_state = state()
  cleanup_buffers()

  ensure_panel()

  if is_managed_terminal(terminal_state.current) then
    set_terminal_buffer(terminal_state.current)
    return
  end

  if #terminal_state.buffers > 0 then
    set_terminal_buffer(terminal_state.buffers[#terminal_state.buffers])
    return
  end

  M.new()
end

function M.focus_buffer()
  local target = find_workspace_window()
  if not target then
    vim.notify("No workspace window available", vim.log.levels.WARN)
    return
  end

  vim.api.nvim_set_current_win(target)
end

function M.new()
  local winid = ensure_panel()

  with_redirect_suspended(function()
    local bufnr = create_terminal_buffer()
    vim.b[bufnr].terminal_panel_managed = true
    register_terminal(bufnr)
    set_terminal_buffer(bufnr)
  end)
end

function M.cycle(step)
  local terminal_state = state()
  cleanup_buffers()

  if #terminal_state.buffers == 0 then
    M.new()
    return
  end

  local index = current_terminal_index() or 1
  local target = ((index - 1 + step) % #terminal_state.buffers) + 1
  M.select(target)
end

function M.setup()
  map("t", "<Esc><Esc><Esc>", [[<C-\><C-n>]], { desc = "Exit terminal mode" })
  map("t", "<M-h>", function()
    M.cycle(-1)
  end, { desc = "Previous terminal tab" })
  map("t", "<M-l>", function()
    M.cycle(1)
  end, { desc = "Next terminal tab" })
  map("t", "<M-b>", function()
    M.focus_buffer()
  end, { desc = "Focus workspace buffer" })

  map("n", "<M-t>", function()
    M.open()
  end, { desc = "Focus terminal tab" })

  map({ "n", "t" }, "<leader>tt", function()
    M.open()
  end, { desc = "Open terminal tabs" })

  map({ "n", "t" }, "<leader>tn", function()
    M.new()
  end, { desc = "New terminal tab" })

  map({ "n", "t" }, "<leader>th", function()
    M.cycle(-1)
  end, { desc = "Previous terminal tab" })

  map({ "n", "t" }, "<leader>tl", function()
    M.cycle(1)
  end, { desc = "Next terminal tab" })
  map({ "n", "t" }, "<leader>tb", function()
    M.focus_buffer()
  end, { desc = "Focus workspace buffer" })

  vim.api.nvim_create_user_command("TerminalPanel", function()
    M.open()
  end, {
    desc = "Open the right-side terminal tabs",
  })

  vim.api.nvim_create_user_command("TerminalPanelNew", function()
    M.new()
  end, {
    desc = "Create a new terminal tab in the right-side terminal area",
  })

  vim.api.nvim_create_autocmd("TermOpen", {
    group = augroup,
    desc = "Register managed terminal buffers",
    callback = function(event)
      if vim.b[event.buf].terminal_panel_managed == true or is_terminal_window(vim.api.nvim_get_current_win()) then
        register_terminal(event.buf)
      end
    end,
  })

  vim.api.nvim_create_autocmd({ "BufEnter", "TermEnter" }, {
    group = augroup,
    desc = "Keep terminal tabs state in sync",
    callback = function(event)
      local terminal_state = state()
      local winid = vim.api.nvim_get_current_win()

      if is_workspace_window(winid) then
        record_workspace_window(winid)
      end

      if not is_panel_window(winid) or terminal_state.suspend_redirect then
        return
      end

      if is_tabbar_window(winid) then
        if not is_tabbar_buffer(event.buf) then
          restore_tabbar()
          return
        end

        restore_tabbar()
        return
      end

      if is_terminal_buffer(event.buf) then
        register_terminal(event.buf)
        apply_terminal_style(winid)
        return
      end

      if is_managed_terminal(terminal_state.current) then
        set_terminal_buffer(terminal_state.current, { enter_insert = false })
      elseif #terminal_state.buffers > 0 then
        set_terminal_buffer(terminal_state.buffers[#terminal_state.buffers], { enter_insert = false })
      else
        M.new()
      end
    end,
  })

  vim.api.nvim_create_autocmd("WinEnter", {
    group = augroup,
    desc = "Track the last focused workspace window",
    callback = function()
      record_workspace_window(vim.api.nvim_get_current_win())
    end,
  })

  vim.api.nvim_create_autocmd({ "BufDelete", "BufWipeout" }, {
    group = augroup,
    desc = "Prune closed terminal buffers from the terminal tabs",
    callback = function(event)
      local terminal_state = state()

      if event.buf == terminal_state.tab_bufnr then
        terminal_state.tab_bufnr = nil
      end

      cleanup_buffers()
      update_tabbar()
    end,
  })

  vim.api.nvim_create_autocmd("WinClosed", {
    group = augroup,
    desc = "Forget closed terminal tabs windows",
    callback = function(event)
      local terminal_state = state()
      local winid = tonumber(event.match)

      if winid == terminal_state.tab_winid then
        terminal_state.tab_winid = nil
      end

      if winid == terminal_state.term_winid then
        terminal_state.term_winid = nil
      end
    end,
  })
end

return M

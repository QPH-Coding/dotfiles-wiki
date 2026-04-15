local M = {}

local registry = {}
local registry_order = 0
local setup_done = false

local function merge_opts(...)
  local merged = {}

  for index = 1, select("#", ...) do
    local value = select(index, ...)
    if value then
      merged = vim.tbl_extend("force", merged, value)
    end
  end

  return merged
end

local function normalize_modes(mode)
  if type(mode) == "table" then
    return vim.deepcopy(mode)
  end

  return { mode }
end

local function mode_string(mode)
  return table.concat(normalize_modes(mode), ",")
end

local function format_description(entry)
  local description = entry.desc

  if entry.detail and entry.detail ~= "" then
    description = description .. " [" .. entry.detail .. "]"
  end

  if entry.scope == "buffer-local" then
    description = description .. " {buffer-local}"
  end

  return description
end

local function sorted_entries(module_filter)
  local entries = {}

  for _, entry in pairs(registry) do
    if not module_filter or entry.module:lower():find(module_filter:lower(), 1, true) then
      table.insert(entries, entry)
    end
  end

  table.sort(entries, function(left, right)
    if left.module ~= right.module then
      return left.module < right.module
    end

    if left.mode ~= right.mode then
      return left.mode < right.mode
    end

    if left.lhs ~= right.lhs then
      return left.lhs < right.lhs
    end

    return left.order < right.order
  end)

  return entries
end

local function max_width(entries, field, min_width, max_allowed)
  local width = min_width

  for _, entry in ipairs(entries) do
    width = math.max(width, #entry[field])
  end

  return math.min(width, max_allowed)
end

local function record(module, mode, lhs, opts)
  opts = opts or {}

  if opts.cheatsheet == false then
    return
  end

  local desc = opts.desc or opts.label or opts.detail or "No description"
  local scope = opts.scope or (opts.buffer and "buffer-local" or "global")
  local mode_label = mode_string(mode)
  local id = table.concat({
    module,
    mode_label,
    lhs,
    scope,
  }, "::")

  local existing = registry[id]
  if not existing then
    registry_order = registry_order + 1
  end

  registry[id] = {
    order = existing and existing.order or registry_order,
    module = module,
    mode = mode_label,
    lhs = lhs,
    desc = desc,
    detail = opts.detail,
    scope = scope,
  }
end

local function render_lines(module_filter)
  local entries = sorted_entries(module_filter)
  local lhs_width = max_width(entries, "lhs", 16, 28)
  local lines = {
    "Neovim Keymap Cheatsheet",
    module_filter and ("Module filter: " .. module_filter) or "Grouped by module. Use / to search in this window.",
    "Use :CheatsheetSearch for fuzzy lookup.",
  }

  if #entries == 0 then
    table.insert(lines, "")
    table.insert(lines, "No registered keymaps matched the current filter.")
    return lines
  end

  local current_module = nil
  for _, entry in ipairs(entries) do
    if entry.module ~= current_module then
      table.insert(lines, "")
      table.insert(lines, "[" .. entry.module .. "]")
      current_module = entry.module
    end

    table.insert(lines, string.format("  %-5s %-" .. lhs_width .. "s %s", entry.mode, entry.lhs, format_description(entry)))
  end

  return lines
end

function M.map(module, mode, lhs, rhs, opts)
  local map_opts = merge_opts(opts)
  vim.keymap.set(mode, lhs, rhs, map_opts)
  record(module, mode, lhs, map_opts)
end

function M.mapper(module, defaults)
  return function(mode, lhs, rhs, opts)
    M.map(module, mode, lhs, rhs, merge_opts(defaults, opts))
  end
end

function M.buffer_mapper(module, bufnr, defaults)
  return function(mode, lhs, rhs, opts)
    M.map(module, mode, lhs, rhs, merge_opts(defaults, opts, { buffer = bufnr }))
  end
end

function M.register(module, entries)
  for _, entry in ipairs(entries) do
    record(module, entry.mode, entry.lhs, entry)
  end
end

function M.modules()
  local modules = {}
  local seen = {}

  for _, entry in pairs(registry) do
    if not seen[entry.module] then
      seen[entry.module] = true
      table.insert(modules, entry.module)
    end
  end

  table.sort(modules)

  return modules
end

function M.open(module_filter)
  local lines = render_lines(module_filter)
  local buf = vim.api.nvim_create_buf(false, true)
  local width = 72
  local max_width_allowed = math.max(1, vim.o.columns - 4)

  for _, line in ipairs(lines) do
    width = math.max(width, vim.fn.strdisplaywidth(line) + 4)
  end

  width = math.min(width, max_width_allowed)

  local max_height_allowed = math.max(1, vim.o.lines - 4)
  local height = math.min(#lines, math.min(max_height_allowed, math.max(8, math.floor(vim.o.lines * 0.8))))
  local row = math.max(1, math.floor((vim.o.lines - height) / 2) - 1)
  local col = math.max(0, math.floor((vim.o.columns - width) / 2))
  local win = vim.api.nvim_open_win(buf, true, {
    relative = "editor",
    row = row,
    col = col,
    width = width,
    height = height,
    style = "minimal",
    border = "rounded",
  })

  vim.bo[buf].buftype = "nofile"
  vim.bo[buf].bufhidden = "wipe"
  vim.bo[buf].swapfile = false
  vim.bo[buf].modifiable = true
  vim.bo[buf].filetype = "markdown"

  vim.api.nvim_buf_set_lines(buf, 0, -1, false, lines)
  vim.bo[buf].modifiable = false

  vim.wo[win].wrap = false
  vim.wo[win].cursorline = true

  vim.keymap.set("n", "q", "<cmd>close<CR>", { buffer = buf, nowait = true, silent = true })
  vim.keymap.set("n", "<Esc>", "<cmd>close<CR>", { buffer = buf, nowait = true, silent = true })
end

function M.search()
  local ok, fzf = pcall(require, "fzf-lua")
  if not ok then
    vim.notify("fzf-lua is unavailable, falling back to the grouped cheatsheet", vim.log.levels.WARN)
    M.open()
    return
  end

  local entries = sorted_entries()
  if #entries == 0 then
    vim.notify("No registered keymaps are available for the cheatsheet", vim.log.levels.WARN)
    return
  end

  local module_width = max_width(entries, "module", 12, 18)
  local lhs_width = max_width(entries, "lhs", 14, 24)
  local lines = {
    string.format("%-" .. module_width .. "s | %-5s | %-" .. lhs_width .. "s | %s", "module", "mode", "keymap", "description"),
  }

  for _, entry in ipairs(entries) do
    table.insert(
      lines,
      string.format(
        "%-" .. module_width .. "s | %-5s | %-" .. lhs_width .. "s | %s",
        entry.module,
        entry.mode,
        entry.lhs,
        format_description(entry)
      )
    )
  end

  fzf.fzf_exec(lines, {
    prompt = "Keymaps> ",
    fzf_opts = {
      ["--header-lines"] = "1",
    },
  })
end

function M.setup()
  if setup_done then
    return
  end

  setup_done = true

  vim.api.nvim_create_user_command("Cheatsheet", function(args)
    local module_filter = args.args ~= "" and args.args or nil
    M.open(module_filter)
  end, {
    nargs = "?",
    desc = "Open the grouped keymap cheatsheet",
    complete = function(arg_lead)
      local matches = {}

      for _, module in ipairs(M.modules()) do
        if arg_lead == "" or module:lower():find(arg_lead:lower(), 1, true) then
          table.insert(matches, module)
        end
      end

      return matches
    end,
  })

  vim.api.nvim_create_user_command("CheatsheetSearch", function()
    M.search()
  end, {
    desc = "Search the grouped keymap cheatsheet",
  })
end

return M

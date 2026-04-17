local keymaps = require("core.keymaps")
local treesitter = require("nvim-treesitter")
local uv = vim.uv or vim.loop

local map = keymaps.mapper("Treesitter")
local augroup = vim.api.nvim_create_augroup("dotfiles_wiki_treesitter", { clear = true })

local parser_names = {
  "bash",
  "c",
  "c_sharp",
  "cpp",
  "go",
  "gomod",
  "gosum",
  "gowork",
  "lua",
  "markdown",
  "markdown_inline",
  "python",
  "query",
  "rust",
  "vim",
  "vimdoc",
}

local highlight_filetypes = {
  bash = true,
  c = true,
  cpp = true,
  cs = true,
  go = true,
  gomod = true,
  gosum = true,
  gowork = true,
  help = true,
  lua = true,
  markdown = true,
  python = true,
  query = true,
  rust = true,
  sh = true,
  vim = true,
}

local indent_filetypes = {
  bash = true,
  c = true,
  cpp = true,
  go = true,
  lua = true,
  python = true,
  rust = true,
  sh = true,
  vim = true,
}

local max_file_size = 1024 * 1024
local selection_state = {}

treesitter.setup({
  install_dir = vim.fs.joinpath(vim.fn.stdpath("data"), "site"),
})

local function is_large_file(bufnr)
  local name = vim.api.nvim_buf_get_name(bufnr)
  if name == "" then
    return false
  end

  local stat = uv.fs_stat(name)

  return stat and stat.type == "file" and stat.size > max_file_size
end

local function get_state(bufnr)
  if type(selection_state[bufnr]) ~= "table" then
    selection_state[bufnr] = {
      index = 0,
      stack = {},
    }
  end

  return selection_state[bufnr]
end

local function same_range(left, right)
  if not left or not right then
    return false
  end

  local left_sr, left_sc, left_er, left_ec = left:range()
  local right_sr, right_sc, right_er, right_ec = right:range()

  return left_sr == right_sr and left_sc == right_sc and left_er == right_er and left_ec == right_ec
end

local function selection_end(bufnr, row, col)
  if col > 0 then
    return row, col - 1
  end

  if row == 0 then
    return row, 0
  end

  local previous = vim.api.nvim_buf_get_lines(bufnr, row - 1, row, false)[1] or ""

  return row - 1, math.max(#previous - 1, 0)
end

local function select_node(bufnr, node)
  local start_row, start_col, end_row, end_col = node:range()
  local visual_end_row, visual_end_col = selection_end(bufnr, end_row, end_col)

  vim.fn.setpos("'<", { bufnr, start_row + 1, start_col + 1, 0 })
  vim.fn.setpos("'>", { bufnr, visual_end_row + 1, visual_end_col + 1, 0 })
  vim.api.nvim_win_set_cursor(0, { visual_end_row + 1, visual_end_col })
  vim.cmd("normal! gv")
end

local function current_node(bufnr)
  local parser = vim.treesitter.get_parser(bufnr)
  if not parser then
    return nil
  end

  parser:parse()

  local cursor = vim.api.nvim_win_get_cursor(0)

  return vim.treesitter.get_node({
    bufnr = bufnr,
    ignore_injections = false,
    pos = { cursor[1] - 1, cursor[2] },
  })
end

local function next_parent(node)
  local parent = node and node:parent() or nil

  while parent and same_range(node, parent) do
    parent = parent:parent()
  end

  return parent
end

local function next_scope(node)
  local start_row, _, end_row = node:range()
  local current_span = end_row - start_row
  local parent = next_parent(node)

  while parent do
    local parent_start_row, _, parent_end_row = parent:range()
    if parent_end_row - parent_start_row > current_span then
      return parent
    end

    parent = next_parent(parent)
  end

  return next_parent(node)
end

local function set_selection(bufnr, node)
  local state = get_state(bufnr)

  for index = #state.stack, state.index + 1, -1 do
    state.stack[index] = nil
  end

  state.index = state.index + 1
  state.stack[state.index] = node

  select_node(bufnr, node)
end

local function init_selection()
  local bufnr = vim.api.nvim_get_current_buf()
  local node = current_node(bufnr)

  if not node then
    vim.notify("Tree-sitter node unavailable for current buffer", vim.log.levels.WARN)
    return
  end

  selection_state[bufnr] = {
    index = 0,
    stack = {},
  }

  set_selection(bufnr, node)
end

local function expand_selection(kind)
  local bufnr = vim.api.nvim_get_current_buf()
  local state = get_state(bufnr)

  if state.index == 0 then
    init_selection()
    return
  end

  if state.index < #state.stack then
    state.index = state.index + 1
    select_node(bufnr, state.stack[state.index])
    return
  end

  local current = state.stack[state.index]
  local next_node = kind == "scope" and next_scope(current) or next_parent(current)

  if not next_node then
    return
  end

  set_selection(bufnr, next_node)
end

local function shrink_selection()
  local bufnr = vim.api.nvim_get_current_buf()
  local state = get_state(bufnr)

  if state.index <= 1 then
    return
  end

  state.index = state.index - 1
  select_node(bufnr, state.stack[state.index])
end

vim.api.nvim_create_autocmd("FileType", {
  group = augroup,
  pattern = vim.tbl_keys(highlight_filetypes),
  desc = "Enable Tree-sitter features with a large-file guard",
  callback = function(event)
    if is_large_file(event.buf) then
      return
    end

    local ok = pcall(vim.treesitter.start, event.buf)
    if not ok then
      return
    end

    local filetype = vim.bo[event.buf].filetype
    if indent_filetypes[filetype] then
      vim.bo[event.buf].indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
    end
  end,
})

vim.api.nvim_create_autocmd({ "BufDelete", "BufWipeout", "TextChanged", "TextChangedI" }, {
  group = augroup,
  desc = "Discard stale Tree-sitter selection state",
  callback = function(event)
    selection_state[event.buf] = nil
  end,
})

vim.api.nvim_create_user_command("TSInstallConfigured", function()
  treesitter.install(parser_names)
end, {
  desc = "Install the Tree-sitter parsers declared in this config",
})

map("n", "gnn", init_selection, { desc = "Init selection" })
map("n", "grn", function()
  expand_selection("node")
end, { desc = "Expand to next node" })
map("n", "grc", function()
  expand_selection("scope")
end, { desc = "Expand to current scope" })
map("n", "grm", shrink_selection, { desc = "Shrink selection" })

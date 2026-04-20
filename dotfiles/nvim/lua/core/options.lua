local opt = vim.opt

-- UI and feedback.
opt.number = true
opt.relativenumber = true
opt.signcolumn = "yes"
opt.cursorline = true
opt.termguicolors = true

-- Editing ergonomics and responsiveness.
opt.mouse = "a"
opt.clipboard = "unnamedplus"
opt.undofile = true
opt.confirm = true
opt.updatetime = 200
opt.timeoutlen = 500

-- Indentation defaults for the common case.
opt.expandtab = true
opt.shiftwidth = 2
opt.tabstop = 2
opt.smartindent = true
opt.breakindent = true

-- Search behavior.
opt.ignorecase = true
opt.smartcase = true
opt.inccommand = "split"
opt.hlsearch = true

-- Window navigation and viewport padding.
opt.splitbelow = true
opt.splitright = true
opt.scrolloff = 4
opt.sidescrolloff = 8

-- Completion and rendering.
opt.laststatus = 3
opt.completeopt = { "menu", "menuone", "noselect" }
opt.fillchars = { eob = " " }

-- Session persistence for persistence.nvim.
opt.sessionoptions = {
  "buffers",
  "curdir",
  "folds",
  "globals",
  "help",
  "skiprtp",
  "tabpages",
  "winsize",
}

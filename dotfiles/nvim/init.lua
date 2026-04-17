if not vim.pack then
  error("This config requires Neovim with vim.pack support (Neovim 0.12+).")
end

vim.g.mapleader = " "
vim.g.maplocalleader = ","

require("core.options")
require("core.keymaps").setup()
require("core.editor")
require("core.terminal").setup()

if vim.fn.has("win32") == 1 or vim.fn.has("win64") == 1 then
  vim.g.clipboard = {
    name = "win32yank",
    copy = {
      ["+"] = { "win32yank.exe", "-i", "--crlf" },
      ["*"] = { "win32yank.exe", "-i", "--crlf" },
    },
    paste = {
      ["+"] = { "win32yank.exe", "-o", "--lf" },
      ["*"] = { "win32yank.exe", "-o", "--lf" },
    },
    cache_enabled = false,
  }
end

-- Plugins config

vim.pack.add({
  "https://github.com/Saghen/blink.cmp",
  "https://github.com/akinsho/bufferline.nvim",
  "https://github.com/sainnhe/everforest",
  "https://github.com/MagicDuck/grug-far.nvim",
  "https://github.com/mason-org/mason.nvim",
  "https://github.com/mason-org/mason-lspconfig.nvim",
  "https://github.com/stevearc/conform.nvim",
  "https://github.com/ibhagwan/fzf-lua",
  "https://github.com/stevearc/oil.nvim",
  "https://github.com/nvim-lualine/lualine.nvim",
  "https://github.com/neovim/nvim-lspconfig",
  "https://github.com/nvim-treesitter/nvim-treesitter",
  "https://github.com/folke/persistence.nvim",
}, {
  confirm = false,
  load = true,
})

require("plugins.everforest")

local blink = require("plugins.blink")
require("plugins.bufferline")
require("plugins.conform")
require("plugins.fzf_lua")
require("plugins.grug_far")
require("plugins.lualine")
require("plugins.mason")

local nvim_lspconfig = require("plugins.nvim_lspconfig")
nvim_lspconfig.setup(blink.capabilities)

require("plugins.mason_lspconfig").setup(nvim_lspconfig.server_names)
require("plugins.nvim_treesitter")
require("plugins.oil")
require("plugins.persistence")

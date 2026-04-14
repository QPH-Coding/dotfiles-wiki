require("nvim-treesitter").setup({
  ensure_installed = {
    "bash",
    "lua",
    "markdown",
    "markdown_inline",
    "python",
    "query",
    "rust",
    "vim",
    "vimdoc",
  },
  sync_install = false,
  auto_install = false,
  highlight = {
    enable = true,
    additional_vim_regex_highlighting = false,
  },
  indent = {
    enable = true,
  },
  incremental_selection = {
    enable = true,
    keymaps = {
      init_selection = "gnn",
      node_incremental = "grn",
      scope_incremental = "grc",
      node_decremental = "grm",
    },
  },
})

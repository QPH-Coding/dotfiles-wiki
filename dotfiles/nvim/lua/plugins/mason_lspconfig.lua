local M = {}

function M.setup(server_names)
  require("mason-lspconfig").setup({
    ensure_installed = server_names,
    automatic_enable = server_names,
  })
end

return M

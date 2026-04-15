local map = require("core.keymaps").mapper("Conform")

require("conform").setup({
  formatters_by_ft = {
    lua = { "stylua" },
    sh = { "shfmt" },
    bash = { "shfmt" },
  },
  default_format_opts = {
    lsp_format = "fallback",
  },
  format_on_save = function(bufnr)
    if vim.bo[bufnr].buftype ~= "" then
      return nil
    end

    return {
      lsp_format = "fallback",
      timeout_ms = 500,
    }
  end,
  notify_no_formatters = false,
})

map("n", "<leader>f", function()
  require("conform").format({
    async = true,
    lsp_format = "fallback",
  })
end, { desc = "Format buffer" })

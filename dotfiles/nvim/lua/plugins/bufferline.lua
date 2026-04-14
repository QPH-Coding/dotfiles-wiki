require("bufferline").setup({
  options = {
    diagnostics = "nvim_lsp",
    diagnostics_update_in_insert = false,
    show_buffer_icons = false,
    show_buffer_close_icons = false,
    show_close_icon = false,
    separator_style = "thin",
    always_show_bufferline = true,
    diagnostics_indicator = function(count)
      return "(" .. count .. ")"
    end,
  },
})

local map = vim.keymap.set

map("n", "<S-h>", "<cmd>BufferLineCyclePrev<CR>", { desc = "Previous buffer" })
map("n", "<S-l>", "<cmd>BufferLineCycleNext<CR>", { desc = "Next buffer" })
map("n", "<leader>bp", "<cmd>BufferLinePick<CR>", { desc = "Pick buffer" })

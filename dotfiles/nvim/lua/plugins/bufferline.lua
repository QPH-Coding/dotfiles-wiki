local map = require("core.keymaps").mapper("Bufferline")

require("bufferline").setup({
  options = {
    diagnostics = false,
    show_buffer_icons = false,
    show_buffer_close_icons = false,
    show_close_icon = false,
    separator_style = "thin",
    always_show_bufferline = true,
  },
})

map("n", "<M-h>", "<cmd>BufferLineCyclePrev<CR>", { desc = "Previous buffer" })
map("n", "<M-l>", "<cmd>BufferLineCycleNext<CR>", { desc = "Next buffer" })
map("n", "<leader>bp", "<cmd>BufferLinePick<CR>", { desc = "Pick buffer" })

local map = require("core.keymaps").mapper("Oil")

require("oil").setup({
  default_file_explorer = true,
  columns = {},
  float = {
    border = "rounded",
  },
  keymaps = {
    ["<C-h>"] = false,
    ["<C-l>"] = false,
    ["<C-s>"] = { "actions.select", opts = { horizontal = true } },
    ["<C-v>"] = { "actions.select", opts = { vertical = true } },
  },
  view_options = {
    show_hidden = true,
  },
})

map("n", "_", function()
  require("oil").open()
end, { desc = "Open parent directory" })

map("n", "<leader>fe", function()
  require("oil").toggle_float()
end, { desc = "Toggle file explorer" })
